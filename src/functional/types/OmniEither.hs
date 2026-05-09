-- OmniEither.hs — Pure Functional Error Handling
-- Layer: Functional / Haskell
--
-- Provides a strict, custom implementation of the Either Monad for 
-- short-circuiting error handling paths in OMNI configuration parsers. Zero mock.

module OmniEither (
    OmniEither(..),
    isLeft,
    isRight,
    fromRight,
    fromLeft,
    mapRight,
    mapLeft
) where

import Control.Monad (ap)

-- | Represents a computation that can either fail (Left e) or succeed (Right a).
data OmniEither e a = OmniLeft e | OmniRight a
    deriving (Show, Eq)

instance Functor (OmniEither e) where
    fmap _ (OmniLeft e)  = OmniLeft e
    fmap f (OmniRight a) = OmniRight (f a)

instance Applicative (OmniEither e) where
    pure = OmniRight
    (<*>) = ap

instance Monad (OmniEither e) where
    return = pure
    (OmniLeft e)  >>= _ = OmniLeft e
    (OmniRight a) >>= f = f a

-- | Check if the result is a failure.
isLeft :: OmniEither e a -> Bool
isLeft (OmniLeft _) = True
isLeft _            = False

-- | Check if the result is a success.
isRight :: OmniEither e a -> Bool
isRight (OmniRight _) = True
isRight _             = False

-- | Extract the success value, providing a fallback if failed.
fromRight :: a -> OmniEither e a -> a
fromRight _ (OmniRight a) = a
fromRight def (OmniLeft _) = def

-- | Extract the error value, providing a fallback if succeeded.
fromLeft :: e -> OmniEither e a -> e
fromLeft _ (OmniLeft e) = e
fromLeft def (OmniRight _) = def

-- | Map over the success value (alias for fmap).
mapRight :: (a -> b) -> OmniEither e a -> OmniEither e b
mapRight = fmap

-- | Map over the error value.
mapLeft :: (e1 -> e2) -> OmniEither e1 a -> OmniEither e2 a
mapLeft f (OmniLeft e)  = OmniLeft (f e)
mapLeft _ (OmniRight a) = OmniRight a
