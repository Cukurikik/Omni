-- OMNI Compute — Haskell Pure Functional Transformer Components
-- Type-safe, pure functional attention and normalization.

module Omni.Transformer where

import Data.List (foldl', transpose)

-- | Vector operations
type Vec = [Double]
type Matrix = [Vec]

dotProduct :: Vec -> Vec -> Double
dotProduct a b = sum $ zipWith (*) a b

matVecMul :: Matrix -> Vec -> Vec
matVecMul m v = map (`dotProduct` v) m

matMul :: Matrix -> Matrix -> Matrix
matMul a b = let bt = transpose b in map (\row -> map (dotProduct row) bt) a

vecScale :: Double -> Vec -> Vec
vecScale s = map (* s)

vecAdd :: Vec -> Vec -> Vec
vecAdd = zipWith (+)

-- | Softmax
softmax :: Vec -> Vec
softmax xs = let m = maximum xs
                 exps = map (\x -> exp (x - m)) xs
                 s = sum exps
             in map (/ s) exps

-- | Layer normalization
layerNorm :: Double -> Vec -> Vec -> Vec -> Vec
layerNorm eps gamma beta x =
  let mu = sum x / fromIntegral (length x)
      variance = sum (map (\xi -> (xi - mu)^2) x) / fromIntegral (length x)
      invStd = 1.0 / sqrt (variance + eps)
  in zipWith3 (\g b xi -> g * (xi - mu) * invStd + b) gamma beta x

-- | RMS normalization
rmsNorm :: Double -> Vec -> Vec -> Vec
rmsNorm eps weight x =
  let ss = sum (map (^2) x) / fromIntegral (length x)
      invRms = 1.0 / sqrt (ss + eps)
  in zipWith (\w xi -> w * xi * invRms) weight x

-- | GELU activation
gelu :: Double -> Double
gelu x = 0.5 * x * (1.0 + tanh (sqrt (2.0 / pi) * (x + 0.044715 * x^3)))

-- | Single attention head
singleHeadAttention :: Matrix -> Matrix -> Matrix -> Matrix -> Matrix
singleHeadAttention wQ wK wV xs =
  let queries = map (matVecMul wQ) xs
      keys    = map (matVecMul wK) xs
      values  = map (matVecMul wV) xs
      dk      = fromIntegral (length (head queries))
      scale   = 1.0 / sqrt dk
      scores  = [[dotProduct q k * scale | k <- keys] | q <- queries]
      attnWeights = map softmax scores
      output  = [foldl' vecAdd (replicate (length (head values)) 0)
                   (zipWith vecScale aw values)
                | aw <- attnWeights]
  in output

-- | Feed-forward network
feedForward :: Matrix -> Vec -> Matrix -> Vec -> Vec -> Vec
feedForward w1 b1 w2 b2 x =
  let hidden = vecAdd (matVecMul w1 x) b1
      activated = map gelu hidden
  in vecAdd (matVecMul w2 activated) b2

-- | Transformer block (pre-norm)
transformerBlock :: Matrix -> Matrix -> Matrix -> Matrix -> Vec -> Matrix -> Vec -> Matrix -> Vec -> Double -> Vec -> Vec
transformerBlock wQ wK wV wO gammaA w1 b1 w2 b2 eps x =
  let normed = layerNorm eps gammaA (replicate (length x) 0) x
      attended = head (singleHeadAttention wQ wK wV [normed])
      projected = matVecMul wO attended
      residual1 = vecAdd x projected
  in residual1
