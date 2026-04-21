-- ===========================================================================
-- OMNI STM ENGINE (SEMESTER 3 — BATCH 38.5)
-- ===========================================================================
-- Absorbed From  : GHC STM + stm-containers + broadcast-chan
-- Logic Inherited: Haskell / Functional Layer (Software Transactional Memory)
-- ===========================================================================
--
-- By studying GHC's STM implementation, Mother learned:
--   1. TVar provides atomic, composable transactions
--   2. retry/orElse enable declarative blocking
--   3. Transactions are optimistically executed, rolled back on conflict
--   4. No deadlocks — STM guarantees progress
--   5. Composability: small transactions combine into larger ones

{-# LANGUAGE ScopedTypeVariables #-}
{-# LANGUAGE DeriveGeneric #-}

module OmniSTMEngine
  ( -- * Core Types
    OmniAccount(..)
  , OmniBank
  , TransferResult(..)
  , BankError(..)
    -- * Bank Operations
  , createBank
  , createAccount
  , getBalance
  , deposit
  , withdraw
  , transfer
  , totalAssets
    -- * Bounded Channel (STM-based)
  , OmniChannel
  , newChannel
  , writeChannel
  , readChannel
  , channelSize
    -- * Read-Write Lock (STM-based)
  , OmniRWLock
  , newRWLock
  , acquireRead
  , releaseRead
  , acquireWrite
  , releaseWrite
    -- * Diagnostics
  , bankDiagnostics
  ) where

import Control.Concurrent.STM
import Control.Monad (when, forM)
import Data.Map.Strict (Map)
import qualified Data.Map.Strict as Map
import Data.IORef
import GHC.Generics (Generic)

-- ============================================================
-- PART 1: STM-Based Bank (Composable Transactions)
-- ============================================================

-- | A bank account with STM-protected balance.
data OmniAccount = OmniAccount
  { accountId      :: !Int
  , accountName    :: !String
  , accountBalance :: !(TVar Double)
  }

-- | Transfer result type (monadic error handling).
data TransferResult
  = TransferOk
  | TransferFailed BankError
  deriving (Show)

data BankError
  = InsufficientFunds { errorAccount :: Int, errorAmount :: Double }
  | AccountNotFound Int
  | NegativeAmount Double
  | SameAccountTransfer
  deriving (Show)

-- | Bank state with STM-protected account map.
data OmniBank = OmniBank
  { bankAccounts     :: !(TVar (Map Int OmniAccount))
  , bankNextId       :: !(TVar Int)
  , bankTotalTx      :: !(IORef Int)
  , bankTotalDeposit :: !(IORef Int)
  , bankTotalWithdraw:: !(IORef Int)
  , bankTotalTransfer:: !(IORef Int)
  }

-- | Create a new empty bank.
createBank :: IO OmniBank
createBank = do
  accounts   <- newTVarIO Map.empty
  nextId     <- newTVarIO 1
  totalTx    <- newIORef 0
  totalDep   <- newIORef 0
  totalWith  <- newIORef 0
  totalTrans <- newIORef 0
  return OmniBank
    { bankAccounts      = accounts
    , bankNextId        = nextId
    , bankTotalTx       = totalTx
    , bankTotalDeposit  = totalDep
    , bankTotalWithdraw = totalWith
    , bankTotalTransfer = totalTrans
    }

-- | Create a new account with initial balance.
createAccount :: OmniBank -> String -> Double -> IO Int
createAccount bank name initialBalance = atomically $ do
  aid <- readTVar (bankNextId bank)
  writeTVar (bankNextId bank) (aid + 1)
  balVar <- newTVar initialBalance
  let account = OmniAccount aid name balVar
  modifyTVar' (bankAccounts bank) (Map.insert aid account)
  return aid

-- | Get account balance (STM transaction).
getBalance :: OmniBank -> Int -> IO (Either BankError Double)
getBalance bank aid = atomically $ do
  accounts <- readTVar (bankAccounts bank)
  case Map.lookup aid accounts of
    Nothing  -> return $ Left (AccountNotFound aid)
    Just acc -> do
      bal <- readTVar (accountBalance acc)
      return $ Right bal

-- | Deposit into an account.
deposit :: OmniBank -> Int -> Double -> IO (Either BankError Double)
deposit bank aid amount
  | amount < 0 = return $ Left (NegativeAmount amount)
  | otherwise = do
      result <- atomically $ do
        accounts <- readTVar (bankAccounts bank)
        case Map.lookup aid accounts of
          Nothing  -> return $ Left (AccountNotFound aid)
          Just acc -> do
            bal <- readTVar (accountBalance acc)
            let newBal = bal + amount
            writeTVar (accountBalance acc) newBal
            return $ Right newBal
      case result of
        Right _ -> modifyIORef' (bankTotalDeposit bank) (+1)
        _       -> return ()
      modifyIORef' (bankTotalTx bank) (+1)
      return result

-- | Withdraw from an account.
withdraw :: OmniBank -> Int -> Double -> IO (Either BankError Double)
withdraw bank aid amount
  | amount < 0 = return $ Left (NegativeAmount amount)
  | otherwise = do
      result <- atomically $ do
        accounts <- readTVar (bankAccounts bank)
        case Map.lookup aid accounts of
          Nothing  -> return $ Left (AccountNotFound aid)
          Just acc -> do
            bal <- readTVar (accountBalance acc)
            if bal < amount
              then return $ Left (InsufficientFunds aid amount)
              else do
                writeTVar (accountBalance acc) (bal - amount)
                return $ Right (bal - amount)
      case result of
        Right _ -> modifyIORef' (bankTotalWithdraw bank) (+1)
        _       -> return ()
      modifyIORef' (bankTotalTx bank) (+1)
      return result

-- | Atomically transfer between two accounts.
-- This is the KEY demonstration: two TVar reads + two writes
-- in a SINGLE atomic transaction — no deadlocks possible.
transfer :: OmniBank -> Int -> Int -> Double -> IO TransferResult
transfer bank fromId toId amount
  | fromId == toId = return $ TransferFailed SameAccountTransfer
  | amount < 0     = return $ TransferFailed (NegativeAmount amount)
  | otherwise = do
      result <- atomically $ do
        accounts <- readTVar (bankAccounts bank)
        case (Map.lookup fromId accounts, Map.lookup toId accounts) of
          (Nothing, _) -> return $ TransferFailed (AccountNotFound fromId)
          (_, Nothing) -> return $ TransferFailed (AccountNotFound toId)
          (Just from, Just to) -> do
            fromBal <- readTVar (accountBalance from)
            if fromBal < amount
              then return $ TransferFailed (InsufficientFunds fromId amount)
              else do
                toBal <- readTVar (accountBalance to)
                writeTVar (accountBalance from) (fromBal - amount)
                writeTVar (accountBalance to)   (toBal + amount)
                return TransferOk
      case result of
        TransferOk -> modifyIORef' (bankTotalTransfer bank) (+1)
        _          -> return ()
      modifyIORef' (bankTotalTx bank) (+1)
      return result

-- | Sum of all account balances (consistent snapshot via STM).
totalAssets :: OmniBank -> IO Double
totalAssets bank = atomically $ do
  accounts <- readTVar (bankAccounts bank)
  balances <- mapM (readTVar . accountBalance) (Map.elems accounts)
  return $ sum balances

-- ============================================================
-- PART 2: STM Bounded Channel
-- ============================================================

-- | Bounded FIFO channel implemented with STM.
data OmniChannel a = OmniChannel
  { chanBuffer   :: !(TVar [a])
  , chanCapacity :: !Int
  , chanSize     :: !(TVar Int)
  , chanSent     :: !(IORef Int)
  , chanRecvd    :: !(IORef Int)
  }

newChannel :: Int -> IO (OmniChannel a)
newChannel capacity = do
  buf    <- newTVarIO []
  sz     <- newTVarIO 0
  sent   <- newIORef 0
  recvd  <- newIORef 0
  return OmniChannel
    { chanBuffer   = buf
    , chanCapacity = capacity
    , chanSize     = sz
    , chanSent     = sent
    , chanRecvd    = recvd
    }

-- | Write to channel, blocks (retries) if full.
writeChannel :: OmniChannel a -> a -> IO ()
writeChannel ch val = do
  atomically $ do
    sz <- readTVar (chanSize ch)
    when (sz >= chanCapacity ch) retry  -- Block until space available
    modifyTVar' (chanBuffer ch) (++ [val])
    writeTVar (chanSize ch) (sz + 1)
  modifyIORef' (chanSent ch) (+1)

-- | Read from channel, blocks (retries) if empty.
readChannel :: OmniChannel a -> IO a
readChannel ch = do
  val <- atomically $ do
    buf <- readTVar (chanBuffer ch)
    case buf of
      []     -> retry  -- Block until data available
      (x:xs) -> do
        writeTVar (chanBuffer ch) xs
        modifyTVar' (chanSize ch) (subtract 1)
        return x
  modifyIORef' (chanRecvd ch) (+1)
  return val

channelSize :: OmniChannel a -> IO Int
channelSize ch = readTVarIO (chanSize ch)

-- ============================================================
-- PART 3: STM Read-Write Lock
-- ============================================================

data OmniRWLock = OmniRWLock
  { rwReaders :: !(TVar Int)
  , rwWriter  :: !(TVar Bool)
  }

newRWLock :: IO OmniRWLock
newRWLock = do
  readers <- newTVarIO 0
  writer  <- newTVarIO False
  return OmniRWLock readers writer

acquireRead :: OmniRWLock -> IO ()
acquireRead lock = atomically $ do
  w <- readTVar (rwWriter lock)
  when w retry  -- Wait if writer active
  modifyTVar' (rwReaders lock) (+1)

releaseRead :: OmniRWLock -> IO ()
releaseRead lock = atomically $
  modifyTVar' (rwReaders lock) (subtract 1)

acquireWrite :: OmniRWLock -> IO ()
acquireWrite lock = atomically $ do
  w <- readTVar (rwWriter lock)
  when w retry  -- Wait if another writer active
  r <- readTVar (rwReaders lock)
  when (r > 0) retry  -- Wait if readers active
  writeTVar (rwWriter lock) True

releaseWrite :: OmniRWLock -> IO ()
releaseWrite lock = atomically $
  writeTVar (rwWriter lock) False

-- ============================================================
-- Diagnostics
-- ============================================================

bankDiagnostics :: OmniBank -> IO [(String, String)]
bankDiagnostics bank = do
  numAccounts <- atomically $ Map.size <$> readTVar (bankAccounts bank)
  assets      <- totalAssets bank
  totalTx     <- readIORef (bankTotalTx bank)
  totalDep    <- readIORef (bankTotalDeposit bank)
  totalWith   <- readIORef (bankTotalWithdraw bank)
  totalTrans  <- readIORef (bankTotalTransfer bank)
  return
    [ ("engine",           "OmniSTMEngine")
    , ("layer",            "Haskell Functional")
    , ("num_accounts",     show numAccounts)
    , ("total_assets",     show assets)
    , ("total_transactions", show totalTx)
    , ("total_deposits",   show totalDep)
    , ("total_withdraws",  show totalWith)
    , ("total_transfers",  show totalTrans)
    , ("learned_logic",    "tvar-atomic-composable,"
                        ++ "retry-declarative-blocking,"
                        ++ "orElse-alternative-transaction,"
                        ++ "optimistic-execution-rollback,"
                        ++ "deadlock-free-guarantee,"
                        ++ "consistent-snapshot-read,"
                        ++ "stm-bounded-channel,"
                        ++ "stm-rwlock-readers-writer")
    ]
