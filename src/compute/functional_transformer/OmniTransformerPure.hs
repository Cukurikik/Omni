-- OmniTransformerPure.hs — Pure Functional Transformer
-- Inspired by: Functional programming paradigm for Memformer
-- Layer: Functional / Haskell
--
-- Purely functional transformer implementation demonstrating
-- immutable data flow, monadic composition, and type-safe attention.

module OmniTransformerPure
  ( TransformerConfig(..)
  , Embedding(..)
  , AttentionOutput(..)
  , TransformerOutput(..)
  , dotProductAttention
  , multiHeadAttention
  , feedForward
  , transformerLayer
  , transformerEncoder
  , softmax
  , layerNorm
  , residualAdd
  ) where

import Data.List (transpose)

-- | Configuration for transformer
data TransformerConfig = TransformerConfig
  { cfgDim        :: Int
  , cfgHeads      :: Int
  , cfgFFMult     :: Int
  , cfgDropout    :: Double
  , cfgMaxSeqLen  :: Int
  , cfgVocabSize  :: Int
  } deriving (Show)

-- | Embedding representation
data Embedding = Embedding
  { embValues :: [[Double]]  -- (seq_len, dim)
  , embSeqLen :: Int
  , embDim    :: Int
  } deriving (Show)

-- | Attention computation output
data AttentionOutput = AttentionOutput
  { attnValues  :: [[Double]]
  , attnWeights :: [[Double]]
  } deriving (Show)

-- | Full transformer output
data TransformerOutput = TransformerOutput
  { transValues    :: [[Double]]
  , transLayerOuts :: [[[Double]]]  -- outputs of each layer
  } deriving (Show)

-- | Numerically stable softmax over a vector
softmax :: [Double] -> [Double]
softmax xs =
  let maxVal = maximum xs
      exps = map (\x -> exp (x - maxVal)) xs
      sumExps = sum exps
  in map (/ sumExps) exps

-- | Dot product between two vectors
dot :: [Double] -> [Double] -> Double
dot xs ys = sum $ zipWith (*) xs ys

-- | Matrix multiply: (M x K) * (K x N) -> (M x N)
matMul :: [[Double]] -> [[Double]] -> [[Double]]
matMul a b =
  let bt = transpose b
  in map (\row -> map (dot row) bt) a

-- | Scale a vector
scaleVec :: Double -> [Double] -> [Double]
scaleVec s = map (* s)

-- | Layer normalization
layerNorm :: [Double] -> [Double]
layerNorm xs =
  let n = fromIntegral (length xs)
      mean = sum xs / n
      centered = map (\x -> x - mean) xs
      variance = sum (map (\x -> x * x) centered) / n
      std = sqrt (variance + 1e-6)
  in map (/ std) centered

-- | Apply layer norm to each position in sequence
layerNormSeq :: [[Double]] -> [[Double]]
layerNormSeq = map layerNorm

-- | Residual addition
residualAdd :: [[Double]] -> [[Double]] -> [[Double]]
residualAdd = zipWith (zipWith (+))

-- | Scaled dot-product attention
-- Q, K, V are (seq_len, head_dim)
dotProductAttention :: [[Double]] -> [[Double]] -> [[Double]] -> AttentionOutput
dotProductAttention queries keys values =
  let headDim = length (head queries)
      scale = 1.0 / sqrt (fromIntegral headDim)
      -- Compute attention scores: Q * K^T / sqrt(d_k)
      scores = map (\q -> map (\k -> dot q k * scale) keys) queries
      -- Apply softmax to each row
      weights = map softmax scores
      -- Weighted sum of values
      attended = map (\w -> foldl1 (zipWith (+)) (zipWith scaleVec w values)) weights
  in AttentionOutput attended weights

-- | Split embedding into heads
splitHeads :: Int -> [[Double]] -> [[[Double]]]
splitHeads numHeads seqVecs =
  let headDim = length (head seqVecs) `div` numHeads
      splitVec v = [take headDim (drop (h * headDim) v) | h <- [0..numHeads-1]]
  in transpose [splitVec v | v <- seqVecs]

-- | Concatenate heads back
concatHeads :: [[[Double]]] -> [[Double]]
concatHeads headOutputs =
  let transposed = transpose headOutputs
  in map concat transposed

-- | Multi-head attention
multiHeadAttention :: Int -> [[Double]] -> [[Double]] -> [[Double]] -> AttentionOutput
multiHeadAttention numHeads queries keys values =
  let qHeads = splitHeads numHeads queries
      kHeads = splitHeads numHeads keys
      vHeads = splitHeads numHeads values
      headResults = zipWith3 dotProductAttention qHeads kHeads vHeads
      concatenated = concatHeads (map attnValues headResults)
      -- Average attention weights across heads for visualization
      avgWeights = if null headResults then []
                   else let ws = map attnWeights headResults
                            n = fromIntegral (length ws) :: Double
                        in foldl1 (zipWith (zipWith (+))) ws
                           |> map (map (/ n))
  in AttentionOutput concatenated avgWeights
  where
    (|>) x f = f x

-- | Feed-forward network: Linear -> GELU -> Linear
feedForward :: Int -> [[Double]] -> [[Double]]
feedForward ffDim inputs =
  let dim = length (head inputs)
      -- Simplified: project up, apply activation, project down
      -- In production, use learned weight matrices
      projected = map (\v -> take ffDim (cycle v)) inputs
      activated = map (map gelu) projected
      output = map (\v -> take dim (cycle v)) activated
  in output

-- | GELU activation approximation
gelu :: Double -> Double
gelu x = 0.5 * x * (1.0 + tanh (sqrt (2.0 / pi) * (x + 0.044715 * x * x * x)))

-- | Single transformer layer: LayerNorm -> MHA -> Residual -> LayerNorm -> FF -> Residual
transformerLayer :: Int -> Int -> [[Double]] -> [[Double]]
transformerLayer numHeads ffDim input =
  let normed1 = layerNormSeq input
      attnOut = attnValues $ multiHeadAttention numHeads normed1 normed1 normed1
      residual1 = residualAdd input attnOut
      normed2 = layerNormSeq residual1
      ffOut = feedForward ffDim normed2
      residual2 = residualAdd residual1 ffOut
  in residual2

-- | Stack of transformer layers
transformerEncoder :: TransformerConfig -> [[Double]] -> TransformerOutput
transformerEncoder config input =
  let numLayers = 6  -- default depth
      heads = cfgHeads config
      ffDim = cfgDim config * cfgFFMult config
      (finalOut, layerOuts) = foldl
        (\(current, outs) _ ->
          let next = transformerLayer heads ffDim current
          in (next, outs ++ [next]))
        (input, [])
        [1..numLayers]
  in TransformerOutput
      { transValues = layerNormSeq finalOut
      , transLayerOuts = layerOuts
      }
