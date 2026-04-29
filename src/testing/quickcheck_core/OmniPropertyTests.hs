module OmniPropertyTests where

import Test.QuickCheck

-- | Omni QuickCheck Core (Haskell)
-- | Property-based testing for mathematical invariants.

-- Deterministic reverse function to test invariant
omniReverse :: [a] -> [a]
omniReverse [] = []
omniReverse (x:xs) = omniReverse xs ++ [x]

-- Property: Reversing a list twice yields the original list
prop_reverseTwiceIsOriginal :: [Int] -> Bool
prop_reverseTwiceIsOriginal xs = omniReverse (omniReverse xs) == xs

-- Execution hook for CI runner
runOmniTests :: IO ()
runOmniTests = quickCheck prop_reverseTwiceIsOriginal
