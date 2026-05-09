-- OmniState.hs — Pure State Monad Definition
-- Layer: Functional / Haskell
--
-- Purely functional State Monad implementation ensuring deterministic
-- state transitions for domain simulations and abstract logic flows.

module OmniState (
    State,
    runState,
    execState,
    evalState,
    get,
    put,
    modify
) where

-- A computation that modifies a state of type `s` and yields a result of type `a`
newtype State s a = State { runState :: s -> (a, s) }

instance Functor (State s) where
    fmap f (State g) = State $ \s ->
        let (a, s') = g s
        in (f a, s')

instance Applicative (State s) where
    pure a = State $ \s -> (a, s)
    State f <*> State g = State $ \s ->
        let (func, s') = f s
            (val, s'') = g s'
        in (func val, s'')

instance Monad (State s) where
    return = pure
    State g >>= f = State $ \s ->
        let (a, s') = g s
            State h = f a
        in h s'

-- Extracts only the state
execState :: State s a -> s -> s
execState m s = snd (runState m s)

-- Extracts only the result
evalState :: State s a -> s -> a
evalState m s = fst (runState m s)

-- Fetch the current state
get :: State s s
get = State $ \s -> (s, s)

-- Replace the current state
put :: s -> State s ()
put s = State $ \_ -> ((), s)

-- Modify the current state
modify :: (s -> s) -> State s ()
modify f = do
    s <- get
    put (f s)
