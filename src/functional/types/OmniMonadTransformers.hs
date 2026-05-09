-- OmniMonadTransformers.hs — Monad Transformers
-- Layer: Functional / Haskell
--
-- Composes StateT and ReaderT to create a robust execution environment
-- for OMNI simulations that require both immutable environment config
-- and mutable domain state, without side-effects.

module OmniMonadTransformers where

import Control.Monad.Identity

-- | ReaderT Transformer
newtype ReaderT r m a = ReaderT { runReaderT :: r -> m a }

instance Functor m => Functor (ReaderT r m) where
    fmap f (ReaderT g) = ReaderT $ \r -> fmap f (g r)

instance Applicative m => Applicative (ReaderT r m) where
    pure a = ReaderT $ \_ -> pure a
    ReaderT f <*> ReaderT g = ReaderT $ \r -> f r <*> g r

instance Monad m => Monad (ReaderT r m) where
    return = pure
    ReaderT g >>= f = ReaderT $ \r -> do
        a <- g r
        runReaderT (f a) r

ask :: Monad m => ReaderT r m r
ask = ReaderT return

-- | StateT Transformer
newtype StateT s m a = StateT { runStateT :: s -> m (a, s) }

instance Functor m => Functor (StateT s m) where
    fmap f (StateT g) = StateT $ \s -> fmap (\(a, s') -> (f a, s')) (g s)

instance Monad m => Applicative (StateT s m) where
    pure a = StateT $ \s -> pure (a, s)
    StateT f <*> StateT g = StateT $ \s -> do
        (func, s') <- f s
        (val, s'') <- g s'
        return (func val, s'')

instance Monad m => Monad (StateT s m) where
    return = pure
    StateT g >>= f = StateT $ \s -> do
        (a, s') <- g s
        runStateT (f a) s'

get :: Monad m => StateT s m s
get = StateT $ \s -> return (s, s)

put :: Monad m => s -> StateT s m ()
put s = StateT $ \_ -> return ((), s)

-- | OMNI App Monad Stack (ReaderT Env (StateT State Identity))
type OmniApp env state a = ReaderT env (StateT state Identity) a

runOmniApp :: OmniApp env state a -> env -> state -> (a, state)
runOmniApp app env initialState = runIdentity $ runStateT (runReaderT app env) initialState
