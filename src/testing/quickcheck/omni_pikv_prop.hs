module OmniPiKVProp where
import Test.QuickCheck

-- OMNI MOTHER: Haskell QuickCheck
-- Property-based testing for MoE routing probabilities

prop_ProbabilitiesSumToOne :: [Float] -> Property
prop_ProbabilitiesSumToOne xs = 
    not (null xs) ==> abs (sum (normalize xs) - 1.0) < 0.001
  where
    normalize ys = 
        let s = sum ys
        in if s == 0 then [1.0 / fromIntegral (length ys) | _ <- ys] else map (/ s) ys
