-- OmniMaybe.hs — Pure Functional Optionality
-- Layer: Functional / Haskell
--
-- Provides a strict, custom implementation of the Maybe Monad.
-- Used to represent optional values and safely handle computations that 
-- might fail without throwing runtime exceptions. Zero mock.

module OmniMaybe (
    OmniMaybe(..),
    isJust,
    isNothing,
    fromMaybe,
    mapMaybe,
    catMaybes
) where

import Control.Monad (ap)

-- | Represents an optional value.
data OmniMaybe a = OmniNothing | OmniJust a
    deriving (Show, Eq)

instance Functor OmniMaybe where
    fmap _ OmniNothing  = OmniNothing
    fmap f (OmniJust a) = OmniJust (f a)

instance Applicative OmniMaybe where
    pure = OmniJust
    (<*>) = ap

instance Monad OmniMaybe where
    return = pure
    OmniNothing  >>= _ = OmniNothing
    (OmniJust a) >>= f = f a

-- | Returns True if the value is OmniJust.
isJust :: OmniMaybe a -> Bool
isJust (OmniJust _) = True
isJust OmniNothing  = False

-- | Returns True if the value is OmniNothing.
isNothing :: OmniMaybe a -> Bool
isNothing OmniNothing  = True
isNothing (OmniJust _) = False

-- | Extracts the value, or returns a default if it's OmniNothing.
fromMaybe :: a -> OmniMaybe a -> a
fromMaybe def OmniNothing  = def
fromMaybe _   (OmniJust a) = a

-- | Maps a function returning an OmniMaybe over a list, discarding OmniNothings.
mapMaybe :: (a -> OmniMaybe b) -> [a] -> [b]
mapMaybe _ [] = []
mapMaybe f (x:xs) = 
    case f x of
        OmniNothing  -> mapMaybe f xs
        OmniJust val -> val : mapMaybe f xs

-- | Takes a list of OmniMaybes and returns a list of all the OmniJust values.
catMaybes :: [OmniMaybe a] -> [a]
catMaybes [] = []
catMaybes (OmniNothing : xs)  = catMaybes xs
catMaybes (OmniJust val : xs) = val : catMaybes xs
