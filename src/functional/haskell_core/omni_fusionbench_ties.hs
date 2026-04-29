-- Omni FusionBench TIES Type System (Haskell)
-- Ref: tanganke/fusion_bench — MIT
module Omni.FusionBench.TIES where

data MergeMethod = TaskArithmetic | TIES | DARE | Fisher deriving (Show, Eq)

tiesMerge :: [Double] -> [[Double]] -> Double -> [Double]
tiesMerge base deltas topK =
  let taskVecs = map (\d -> zipWith (-) d base) deltas
      d = length base
  in zipWith (+) base (map (resolveConflict . getColumn taskVecs) [0..d-1])
  where
    getColumn vecs i = map (!! i) (filter (\v -> length v > i) vecs)
    resolveConflict vals =
      let positives = filter (>= 0) vals
          negatives = filter (< 0) vals
      in if length positives >= length negatives
         then if null positives then 0 else sum positives / fromIntegral (length positives)
         else if null negatives then 0 else sum negatives / fromIntegral (length negatives)

dareDropRate :: Double -> Double -> Int -> Double
dareDropRate delta dropRate seed =
  let h = (seed * 2654435761) `mod` 100
  in if fromIntegral h < dropRate * 100 then 0 else delta / max (1 - dropRate) 0.01
