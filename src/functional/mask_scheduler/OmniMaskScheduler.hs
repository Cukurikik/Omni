-- OmniMaskScheduler.hs — Haskell Mask Scheduling for MaskGIT Decoding
-- Inspired by: SoundStorm cosine mask scheduling
-- Layer: Functional / Haskell
--
-- Pure functional mask schedule computation for iterative parallel decoding.
-- Provides cosine, linear, and cubic schedules with confidence-based unmasking.

module OmniMaskScheduler
  ( MaskSchedule(..)
  , ScheduleType(..)
  , MaskState(..)
  , UnmaskDecision(..)
  , cosineSchedule
  , linearSchedule
  , cubicSchedule
  , computeMaskRatio
  , selectTokensToUnmask
  , iterativeDecode
  , initialMaskState
  , stepMaskState
  ) where

import Data.List (sortBy)
import Data.Ord (Down(..))

-- | Schedule type for mask ratio progression
data ScheduleType = Cosine | Linear | Cubic
  deriving (Show, Eq)

-- | Configuration for mask scheduling
data MaskSchedule = MaskSchedule
  { scheduleType    :: ScheduleType
  , totalIterations :: Int
  , gamma           :: Double    -- schedule sharpness parameter
  } deriving (Show)

-- | Current state of the masking process
data MaskState = MaskState
  { currentIteration :: Int
  , maskedPositions  :: [Int]       -- indices still masked
  , unmaskedTokens   :: [(Int, Int)] -- (position, token_id) pairs
  , confidences      :: [Double]    -- confidence per masked position
  } deriving (Show)

-- | Decision for which tokens to unmask
data UnmaskDecision = UnmaskDecision
  { positionsToUnmask :: [Int]
  , tokensAssigned    :: [(Int, Int)]
  , remainingMasked   :: [Int]
  , newMaskRatio      :: Double
  } deriving (Show)

-- | Cosine schedule: mask_ratio = cos(π/2 * t/T)
cosineSchedule :: Int -> Int -> Double
cosineSchedule iteration totalIters =
  let ratio = fromIntegral iteration / fromIntegral totalIters
  in cos (ratio * pi / 2.0)

-- | Linear schedule: mask_ratio = 1 - t/T
linearSchedule :: Int -> Int -> Double
linearSchedule iteration totalIters =
  1.0 - fromIntegral iteration / fromIntegral totalIters

-- | Cubic schedule: mask_ratio = (1 - t/T)^3
cubicSchedule :: Int -> Int -> Double -> Double
cubicSchedule iteration totalIters gamma =
  (1.0 - fromIntegral iteration / fromIntegral totalIters) ** gamma

-- | Compute mask ratio based on schedule type
computeMaskRatio :: MaskSchedule -> Int -> Double
computeMaskRatio schedule iter =
  case scheduleType schedule of
    Cosine -> cosineSchedule iter (totalIterations schedule)
    Linear -> linearSchedule iter (totalIterations schedule)
    Cubic  -> cubicSchedule iter (totalIterations schedule) (gamma schedule)

-- | Select positions to unmask based on model confidence scores
-- Highest confidence positions are unmasked first
selectTokensToUnmask
  :: [(Int, Int, Double)]  -- ^ (position, predicted_token, confidence)
  -> Int                   -- ^ number to unmask
  -> UnmaskDecision
selectTokensToUnmask predictions numToUnmask =
  let sorted = sortBy (\(_, _, c1) (_, _, c2) -> compare (Down c1) (Down c2)) predictions
      (toUnmask, toKeep) = splitAt numToUnmask sorted
      unmaskPositions = map (\(p, _, _) -> p) toUnmask
      unmaskTokens = map (\(p, t, _) -> (p, t)) toUnmask
      remainingPositions = map (\(p, _, _) -> p) toKeep
      remaining = length predictions - numToUnmask
      totalLen = length predictions
      ratio = if totalLen > 0
              then fromIntegral remaining / fromIntegral totalLen
              else 0.0
  in UnmaskDecision
      { positionsToUnmask = unmaskPositions
      , tokensAssigned = unmaskTokens
      , remainingMasked = remainingPositions
      , newMaskRatio = ratio
      }

-- | Create initial fully-masked state
initialMaskState :: Int -> MaskState
initialMaskState seqLen = MaskState
  { currentIteration = 0
  , maskedPositions = [0..seqLen-1]
  , unmaskedTokens = []
  , confidences = replicate seqLen 0.0
  }

-- | Advance mask state by one iteration
stepMaskState
  :: MaskSchedule
  -> MaskState
  -> [(Int, Int, Double)]   -- ^ model predictions: (pos, token, confidence)
  -> MaskState
stepMaskState schedule state predictions =
  let nextIter = currentIteration state + 1
      targetRatio = computeMaskRatio schedule nextIter
      currentMasked = length (maskedPositions state)
      targetMasked = max 0 $ round (fromIntegral currentMasked * targetRatio)
      numToUnmask = currentMasked - targetMasked
      decision = selectTokensToUnmask predictions (max 0 numToUnmask)
  in MaskState
      { currentIteration = nextIter
      , maskedPositions = remainingMasked decision
      , unmaskedTokens = unmaskedTokens state ++ tokensAssigned decision
      , confidences = map (\(_, _, c) -> c) predictions
      }

-- | Run complete iterative decoding process
-- Returns list of (position, token) pairs after all iterations
iterativeDecode
  :: MaskSchedule
  -> Int                                      -- ^ sequence length
  -> (MaskState -> [(Int, Int, Double)])       -- ^ model prediction function
  -> [(Int, Int)]                              -- ^ final token assignments
iterativeDecode schedule seqLen predict =
  let initial = initialMaskState seqLen
      go state
        | currentIteration state >= totalIterations schedule = unmaskedTokens state
        | null (maskedPositions state) = unmaskedTokens state
        | otherwise =
            let preds = predict state
                nextState = stepMaskState schedule state preds
            in go nextState
  in go initial

-- | Compute schedule preview — returns mask ratios for each iteration
schedulePreview :: MaskSchedule -> [Double]
schedulePreview schedule =
  map (\i -> computeMaskRatio schedule i) [0..totalIterations schedule]

-- | Temperature-scaled sampling helper
temperatureScale :: Double -> [Double] -> [Double]
temperatureScale temp logits =
  let scaled = map (/ max temp 1e-10) logits
      maxVal = maximum scaled
      exps = map (\x -> exp (x - maxVal)) scaled
      sumExps = sum exps
  in map (/ sumExps) exps

-- | Top-k filtering: keep only top k values
topKFilter :: Int -> [(Int, Double)] -> [(Int, Double)]
topKFilter k indexed =
  take k $ sortBy (\(_, v1) (_, v2) -> compare (Down v1) (Down v2)) indexed
