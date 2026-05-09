-- OmniReader.hs — Pure Functional Dependency Injection
-- Layer: Functional / Haskell
--
-- Provides a strict, custom implementation of the Reader Monad.
-- Used to pass configuration/environment state implicitly through deeply 
-- nested function calls without mutable global state. Zero mock.

module OmniReader (
    OmniReader(..),
    runReader,
    ask,
    asks,
    local
) where

import Control.Monad (ap)

-- | Represents a computation that reads from an environment of type r to produce a.
newtype OmniReader r a = OmniReader { runReader :: r -> a }

instance Functor (OmniReader r) where
    -- fmap :: (a -> b) -> OmniReader r a -> OmniReader r b
    fmap f (OmniReader g) = OmniReader (\env -> f (g env))

instance Applicative (OmniReader r) where
    -- pure :: a -> OmniReader r a
    pure x = OmniReader (\_ -> x)
    (<*>) = ap

instance Monad (OmniReader r) where
    -- return :: a -> OmniReader r a
    return = pure
    
    -- (>>=) :: OmniReader r a -> (a -> OmniReader r b) -> OmniReader r b
    (OmniReader g) >>= f = OmniReader (\env -> 
        let a = g env
            OmniReader h = f a
        in h env)

-- | Fetches the environment itself.
ask :: OmniReader r r
ask = OmniReader (\env -> env)

-- | Fetches a specific projection of the environment.
asks :: (r -> a) -> OmniReader r a
asks f = OmniReader (\env -> f env)

-- | Executes a computation in a modified environment.
local :: (r -> r) -> OmniReader r a -> OmniReader r a
local f (OmniReader g) = OmniReader (\env -> g (f env))
