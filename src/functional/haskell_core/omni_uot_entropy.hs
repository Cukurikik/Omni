-- Omni UoT Pure Entropy (Haskell)
-- Ref: zhiyuanhubj/UoT — NeurIPS 2024
module Omni.UoT.Entropy where
entropy :: [Double] -> Double
entropy probs = negate $ sum [p * logBase 2 p | p <- probs, p > 1e-12]
informationGain :: [Double] -> [Double] -> Double
informationGain prior posterior = max 0 (entropy prior - entropy posterior)
selectBest :: [[Double]] -> [Double] -> (Int, Double)
selectBest relevances hyps = foldl (\(bi,bg) (i,r) ->
  let post = zipWith (*) hyps r
      s = sum post
      norm = map (/ max s 1e-9) post
      ig = informationGain hyps norm
  in if ig > bg then (i, ig) else (bi, bg)) (0, -1) (zip [0..] relevances)
