-- OmniMonad.hs — Monadic Error Handling Library for OMNI
-- Inspired by: OMNI Section 3.1 mandatory monadic error handling
-- Layer: Functional / Haskell
--
-- Production-grade Result/Either monad with typed errors,
-- railway-oriented programming, and monadic composition.

module OmniMonad
  ( OmniResult(..)
  , OmniError(..)
  , Severity(..)
  , succeed
  , fail'
  , mapResult
  , flatMapResult
  , withDefault
  , fromMaybe'
  , collectResults
  , firstSuccess
  , retry
  , timed
  , validate
  , (>>>=)
  , (|>>)
  ) where

import Data.Time.Clock (getCurrentTime, diffUTCTime, UTCTime)
import Control.Exception (SomeException, try, evaluate)

-- | Severity levels for typed errors
data Severity = Info | Warning | Critical | Fatal
  deriving (Show, Eq, Ord)

-- | Typed error with context
data OmniError = OmniError
  { errCode     :: String
  , errMessage  :: String
  , errSeverity :: Severity
  , errContext  :: [(String, String)]
  } deriving (Show)

-- | Result monad: either success or typed failure
data OmniResult a
  = Success a
  | Failure OmniError
  deriving (Show)

instance Functor OmniResult where
  fmap f (Success a) = Success (f a)
  fmap _ (Failure e) = Failure e

instance Applicative OmniResult where
  pure = Success
  (Success f) <*> (Success a) = Success (f a)
  (Failure e) <*> _           = Failure e
  _           <*> (Failure e) = Failure e

instance Monad OmniResult where
  return = pure
  (Success a) >>= f = f a
  (Failure e) >>= _ = Failure e

-- | Create a success result
succeed :: a -> OmniResult a
succeed = Success

-- | Create a failure result
fail' :: String -> String -> Severity -> OmniResult a
fail' code msg sev = Failure $ OmniError code msg sev []

-- | Map over success value
mapResult :: (a -> b) -> OmniResult a -> OmniResult b
mapResult = fmap

-- | Flat map (bind) for chaining operations
flatMapResult :: (a -> OmniResult b) -> OmniResult a -> OmniResult b
flatMapResult f (Success a) = f a
flatMapResult _ (Failure e) = Failure e

-- | Provide default value for failure
withDefault :: a -> OmniResult a -> a
withDefault _ (Success a) = a
withDefault d (Failure _) = d

-- | Convert Maybe to OmniResult
fromMaybe' :: String -> String -> Maybe a -> OmniResult a
fromMaybe' code msg Nothing  = fail' code msg Warning
fromMaybe' _    _   (Just a) = succeed a

-- | Collect results: all must succeed
collectResults :: [OmniResult a] -> OmniResult [a]
collectResults [] = succeed []
collectResults (Failure e : _) = Failure e
collectResults (Success a : rest) =
  case collectResults rest of
    Success as -> Success (a : as)
    Failure e  -> Failure e

-- | Return first success, or last failure
firstSuccess :: [OmniResult a] -> OmniResult a
firstSuccess [] = fail' "EMPTY" "No results to choose from" Warning
firstSuccess [x] = x
firstSuccess (Success a : _) = Success a
firstSuccess (_ : rest) = firstSuccess rest

-- | Retry an IO action with exponential backoff
retry :: Int -> IO (OmniResult a) -> IO (OmniResult a)
retry 0 action = action
retry n action = do
  result <- action
  case result of
    Success _ -> return result
    Failure _ -> do
      -- Exponential backoff delay would go here in production
      retry (n - 1) action

-- | Time an operation (IO)
timed :: IO (OmniResult a) -> IO (OmniResult (a, Double))
timed action = do
  start <- getCurrentTime
  result <- action
  end <- getCurrentTime
  let elapsed = realToFrac (diffUTCTime end start) :: Double
  return $ fmap (\a -> (a, elapsed * 1000)) result  -- ms

-- | Validate a value against a predicate
validate :: (a -> Bool) -> String -> String -> a -> OmniResult a
validate predicate code msg value
  | predicate value = succeed value
  | otherwise       = fail' code msg Warning

-- | Infix bind operator for railway-oriented programming
(>>>=) :: OmniResult a -> (a -> OmniResult b) -> OmniResult b
(>>>=) = flip flatMapResult

-- | Pipeline operator
(|>>) :: a -> (a -> b) -> b
(|>>) x f = f x

-- | Add context to an error
withContext :: String -> String -> OmniResult a -> OmniResult a
withContext key val (Failure e) =
  Failure $ e { errContext = (key, val) : errContext e }
withContext _ _ success = success

-- | Convert exception to OmniResult
tryOmni :: IO a -> IO (OmniResult a)
tryOmni action = do
  result <- try (evaluate =<< action) :: IO (Either SomeException a)
  case result of
    Right a -> return (succeed a)
    Left ex -> return (fail' "EXCEPTION" (show ex) Critical)

-- | Guard with boolean check
guard' :: Bool -> String -> String -> OmniResult ()
guard' True  _    _   = succeed ()
guard' False code msg = fail' code msg Warning

-- | Pattern: validate and transform in one step
validateAndTransform :: (a -> Bool) -> (a -> b) -> String -> a -> OmniResult b
validateAndTransform check transform errMsg input
  | check input = succeed (transform input)
  | otherwise   = fail' "VALIDATION" errMsg Warning
