-- ===========================================================================
-- OMNI MONAD ENGINE (SEMESTER 3 — BATCH 38.10)
-- ===========================================================================
-- Absorbed From  : Haskell Prelude + mtl + transformers + lens
-- Logic Inherited: Haskell / Functional Layer (Monadic Composition)
-- ===========================================================================
--
-- By studying Haskell monads, Mother learned:
--   1. Monad = Functor + Applicative + bind (>>=) for chaining
--   2. IO monad isolates side effects from pure code
--   3. State monad threads mutable state functionally
--   4. Reader monad provides shared environment
--   5. Writer monad accumulates log output

module Omni.Functional.MonadEngine where

import Data.IORef
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Control.Monad (when, unless, void, forM_, forM)
import Data.Maybe (fromMaybe)

-- ============================================================
-- PART 1: Result Type (Either-based Error Handling)
-- ============================================================

-- | OmniResult: monadic result type for error handling.
data OmniResult e a
  = OmniOk a
  | OmniErr e
  deriving (Show, Eq)

instance Functor (OmniResult e) where
  fmap f (OmniOk a)  = OmniOk (f a)
  fmap _ (OmniErr e) = OmniErr e

instance Applicative (OmniResult e) where
  pure = OmniOk
  (OmniOk f)  <*> (OmniOk a)  = OmniOk (f a)
  (OmniErr e) <*> _            = OmniErr e
  _            <*> (OmniErr e) = OmniErr e

instance Monad (OmniResult e) where
  (OmniOk a)  >>= f = f a
  (OmniErr e) >>= _ = OmniErr e

-- | Map the error type.
mapError :: (e1 -> e2) -> OmniResult e1 a -> OmniResult e2 a
mapError _ (OmniOk a)  = OmniOk a
mapError f (OmniErr e) = OmniErr (f e)

-- | Provide a default value on error.
fromResult :: a -> OmniResult e a -> a
fromResult _ (OmniOk a)  = a
fromResult d (OmniErr _) = d

-- | Convert Maybe to OmniResult.
fromMaybeResult :: e -> Maybe a -> OmniResult e a
fromMaybeResult _ (Just a) = OmniOk a
fromMaybeResult e Nothing  = OmniErr e

-- ============================================================
-- PART 2: Writer Monad (Logging)
-- ============================================================

-- | OmniWriter: accumulates a log alongside a result value.
data OmniWriter w a = OmniWriter { runWriter :: (a, w) }
  deriving (Show)

instance Functor (OmniWriter w) where
  fmap f (OmniWriter (a, w)) = OmniWriter (f a, w)

instance Monoid w => Applicative (OmniWriter w) where
  pure a = OmniWriter (a, mempty)
  (OmniWriter (f, w1)) <*> (OmniWriter (a, w2)) =
    OmniWriter (f a, w1 <> w2)

instance Monoid w => Monad (OmniWriter w) where
  (OmniWriter (a, w1)) >>= f =
    let OmniWriter (b, w2) = f a
    in OmniWriter (b, w1 <> w2)

-- | Write to the log.
tell :: w -> OmniWriter w ()
tell w = OmniWriter ((), w)

-- | Execute and extract the log.
execWriter :: OmniWriter w a -> w
execWriter (OmniWriter (_, w)) = w

-- ============================================================
-- PART 3: Reader Monad (Shared Environment)
-- ============================================================

-- | OmniReader: provides read-only shared environment.
newtype OmniReader r a = OmniReader { runReader :: r -> a }

instance Functor (OmniReader r) where
  fmap f (OmniReader g) = OmniReader (f . g)

instance Applicative (OmniReader r) where
  pure a = OmniReader (const a)
  (OmniReader f) <*> (OmniReader a) = OmniReader (\r -> f r (a r))

instance Monad (OmniReader r) where
  (OmniReader a) >>= f = OmniReader (\r -> runReader (f (a r)) r)

-- | Access the environment.
ask :: OmniReader r r
ask = OmniReader id

-- | Access a projection of the environment.
asks :: (r -> a) -> OmniReader r a
asks f = OmniReader f

-- | Run in a modified environment.
local :: (r -> r) -> OmniReader r a -> OmniReader r a
local f (OmniReader g) = OmniReader (g . f)

-- ============================================================
-- PART 4: State Monad (Mutable State)
-- ============================================================

-- | OmniState: threads mutable state through computation.
newtype OmniState s a = OmniState { runState :: s -> (a, s) }

instance Functor (OmniState s) where
  fmap f (OmniState g) = OmniState (\s -> let (a, s') = g s in (f a, s'))

instance Applicative (OmniState s) where
  pure a = OmniState (\s -> (a, s))
  (OmniState sf) <*> (OmniState sa) = OmniState (\s ->
    let (f, s')  = sf s
        (a, s'') = sa s'
    in (f a, s''))

instance Monad (OmniState s) where
  (OmniState sa) >>= f = OmniState (\s ->
    let (a, s')  = sa s
        OmniState sb = f a
    in sb s')

-- | Get the current state.
getState :: OmniState s s
getState = OmniState (\s -> (s, s))

-- | Set the state.
putState :: s -> OmniState s ()
putState s = OmniState (\_ -> ((), s))

-- | Modify the state.
modifyState :: (s -> s) -> OmniState s ()
modifyState f = OmniState (\s -> ((), f s))

-- | Execute and extract final state.
execState :: OmniState s a -> s -> s
execState (OmniState f) s = snd (f s)

-- | Evaluate and extract the result.
evalState :: OmniState s a -> s -> a
evalState (OmniState f) s = fst (f s)

-- ============================================================
-- PART 5: Composition Utilities
-- ============================================================

-- | Kleisli composition (>=>) for chaining monadic functions.
(>=>) :: Monad m => (a -> m b) -> (b -> m c) -> (a -> m c)
f >=> g = \a -> f a >>= g

-- | Pipe a value through a list of monadic transformations.
pipeline :: Monad m => a -> [a -> m a] -> m a
pipeline initial [] = return initial
pipeline initial (f:fs) = f initial >>= \result -> pipeline result fs

-- | Apply a function N times monadically.
iterateM :: Monad m => Int -> (a -> m a) -> a -> m a
iterateM 0 _ a = return a
iterateM n f a = f a >>= iterateM (n - 1) f

-- | Guard: fail with error if predicate is false.
guardResult :: e -> Bool -> OmniResult e ()
guardResult _ True  = OmniOk ()
guardResult e False = OmniErr e

-- ============================================================
-- Diagnostics
-- ============================================================

diagnostics :: Map String [String]
diagnostics = Map.fromList
  [ ("engine",       ["OmniMonadEngine"])
  , ("layer",        ["Haskell Functional"])
  , ("components",   [ "OmniResult", "OmniWriter", "OmniReader"
                      , "OmniState", "Kleisli", "pipeline"])
  , ("learned_logic", [ "functor-applicative-monad-hierarchy"
                       , "result-either-error-handling"
                       , "writer-accumulate-log"
                       , "reader-shared-environment"
                       , "state-thread-mutable-state"
                       , "kleisli-composition-chaining"
                       , "pipeline-monadic-transforms"
                       , "guard-predicate-short-circuit"])
  ]
