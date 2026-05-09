-- OmniOptics.hs — Functional Lenses for Deep Configuration
-- Layer: Functional / Haskell
--
-- Purely functional lenses allowing safe, immutable updates to deeply 
-- nested application configuration and state records.

module OmniOptics where

import Data.Functor.Identity
import Data.Functor.Const

-- | A Lens s a is a way to view and update an `a` inside an `s`
type Lens s a = forall f. Functor f => (a -> f a) -> s -> f s

-- | Get the value focused by the lens
view :: Lens s a -> s -> a
view lns s = getConst $ lns Const s

-- | Set the value focused by the lens
set :: Lens s a -> a -> s -> s
set lns a s = runIdentity $ lns (\_ -> Identity a) s

-- | Modify the value focused by the lens with a function
over :: Lens s a -> (a -> a) -> s -> s
over lns f s = runIdentity $ lns (Identity . f) s

-- Example Usage Configuration Structures
data SystemConfig = SystemConfig
    { networkCfg :: NetworkConfig
    , dbCfg      :: DatabaseConfig
    } deriving (Show)

data NetworkConfig = NetworkConfig
    { port    :: Int
    , hostIp  :: String
    } deriving (Show)

data DatabaseConfig = DatabaseConfig
    { connectionString :: String
    } deriving (Show)

-- Lenses
networkLens :: Lens SystemConfig NetworkConfig
networkLens f s = (\n -> s { networkCfg = n }) <$> f (networkCfg s)

portLens :: Lens NetworkConfig Int
portLens f n = (\p -> n { port = p }) <$> f (port n)

-- | Composing lenses is just function composition
-- systemPortLens :: Lens SystemConfig Int
-- systemPortLens = networkLens . portLens

-- Example
-- initialConfig = SystemConfig (NetworkConfig 8080 "127.0.0.1") (DatabaseConfig "postgres://...")
-- newConfig = set (networkLens . portLens) 9090 initialConfig
