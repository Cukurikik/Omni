{-# LANGUAGE TupleSections #-}

-- OmniStateTransformer.hs — Pure Functional State Management
-- Layer: Functional / Haskell
--
-- Implements a strict, pure implementation of the State Monad.
-- Allows for composable stateful computations in the OMNI verification layer
-- without relying on side-effectful IO. Zero-mock.

module OmniStateTransformer (
    State(..),
    get,
    put,
    modify,
    evalState,
    execState
) where

import Control.Monad (ap)

-- | The State Monad encapsulating a state transition function.
newtype State s a = State { runState :: s -> (a, s) }

instance Functor (State s) where
    fmap f (State g) = State $ \s -> 
        let (a, s') = g s 
        in (f a, s')

instance Applicative (State s) where
    pure a = State (a,)
    (<*>) = ap

instance Monad (State s) where
    return = pure
    (State h) >>= f = State $ \s -> 
        let (a, s') = h s
            State g = f a
        in g s'

-- | Fetch the current state
get :: State s s
get = State $ \s -> (s, s)

-- | Replace the current state with a new one
put :: s -> State s ()
put s' = State $ \_ -> ((), s')

-- | Modify the current state using a function
modify :: (s -> s) -> State s ()
modify f = do
    s <- get
    put (f s)

-- | Evaluate the state computation, returning only the final value
evalState :: State s a -> s -> a
evalState m s = fst (runState m s)

-- | Execute the state computation, returning only the final state
execState :: State s a -> s -> s
execState m s = snd (runState m s)
