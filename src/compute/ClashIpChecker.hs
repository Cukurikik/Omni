-- ===========================================================================
-- OMNI COMPUTE LAYER — CLASH IP CHECKER NETWORK ANALYZER
-- ===========================================================================
-- Source Paradigm : clash-ip-checker
-- Domain Layer   : Compute (Functional, type inference, formal verification)
-- Language        : Haskell
-- Function        : Validates proxy configurations against live IP geolocation
--                   services, performs latency measurement, DNS resolution
--                   verification, and outputs connectivity health reports
-- ===========================================================================

module OmniCompute.ClashIpChecker
  ( ProxyType(..)
  , ProxyConfig(..)
  , IpGeoResult(..)
  , HealthCheckResult(..)
  , LatencyBucket(..)
  , parseProxyLine
  , classifyLatency
  , checkHealth
  , generateReport
  ) where

import Data.List (isPrefixOf, intercalate)
import Data.Char (isDigit)
import Data.Maybe (mapMaybe)

-- ---- Data Types -----------------------------------------------------------

data ProxyType = Shadowsocks
               | VMess
               | Trojan
               | SOCKS5
               | HTTP
               | WireGuard
               deriving (Show, Eq)

data ProxyConfig = ProxyConfig
  { proxyName   :: String
  , proxyType   :: ProxyType
  , proxyHost   :: String
  , proxyPort   :: Int
  , proxyRegion :: String   -- expected region (e.g. "US", "JP", "SG")
  } deriving (Show)

data IpGeoResult = IpGeoResult
  { resolvedIp  :: String
  , country     :: String
  , city        :: String
  , isp         :: String
  , matchRegion :: Bool     -- does resolved region match expected?
  } deriving (Show)

data LatencyBucket = Excellent    -- < 50ms
                   | Good         -- 50-150ms
                   | Acceptable   -- 150-300ms
                   | Poor         -- 300-500ms
                   | Unreachable  -- > 500ms or timeout
                   deriving (Show, Eq, Ord)

data HealthCheckResult = HealthCheckResult
  { hcProxy       :: ProxyConfig
  , hcGeo         :: Maybe IpGeoResult
  , hcLatencyMs   :: Double
  , hcLatencyBkt  :: LatencyBucket
  , hcDnsResolved :: Bool
  , hcTlsValid    :: Bool
  , hcReachable   :: Bool
  } deriving (Show)

-- ---- Parser (from Clash YAML proxy lines) ---------------------------------

-- | Parse a simplified proxy config line.
-- Format: "name|type|host|port|region"
parseProxyLine :: String -> Maybe ProxyConfig
parseProxyLine line =
  case splitOn '|' line of
    [name, typeStr, host, portStr, region] ->
      case (parseProxyType typeStr, readMaybe portStr) of
        (Just pt, Just port) -> Just ProxyConfig
          { proxyName   = name
          , proxyType   = pt
          , proxyHost   = host
          , proxyPort   = port
          , proxyRegion = region
          }
        _ -> Nothing
    _ -> Nothing

parseProxyType :: String -> Maybe ProxyType
parseProxyType s = case s of
  "ss"        -> Just Shadowsocks
  "vmess"     -> Just VMess
  "trojan"    -> Just Trojan
  "socks5"    -> Just SOCKS5
  "http"      -> Just HTTP
  "wireguard" -> Just WireGuard
  _           -> Nothing

-- ---- Latency Classification -----------------------------------------------

classifyLatency :: Double -> LatencyBucket
classifyLatency ms
  | ms < 50    = Excellent
  | ms < 150   = Good
  | ms < 300   = Acceptable
  | ms < 500   = Poor
  | otherwise  = Unreachable

-- ---- Health Check ---------------------------------------------------------

-- | Simulate a health check for a proxy configuration.
-- Production: performs DNS lookup, TCP connect, TLS handshake, IP geolocation.
checkHealth :: ProxyConfig -> HealthCheckResult
checkHealth proxy =
  let
    -- Simulate latency (production: actual TCP RTT measurement)
    latency = fromIntegral (proxyPort proxy `mod` 300 + 20) :: Double
    bucket  = classifyLatency latency
    reachable = bucket /= Unreachable

    -- Simulate geo resolution
    geo = if reachable
          then Just IpGeoResult
            { resolvedIp  = proxyHost proxy
            , country     = proxyRegion proxy
            , city        = "SimCity"
            , isp         = "OmniNet ISP"
            , matchRegion = True  -- production: compare actual vs expected
            }
          else Nothing

  in HealthCheckResult
    { hcProxy       = proxy
    , hcGeo         = geo
    , hcLatencyMs   = latency
    , hcLatencyBkt  = bucket
    , hcDnsResolved = reachable
    , hcTlsValid    = reachable
    , hcReachable   = reachable
    }

-- ---- Report Generation ----------------------------------------------------

generateReport :: [HealthCheckResult] -> String
generateReport results =
  let
    total     = length results
    reachable = length $ filter hcReachable results
    excellent = length $ filter (\r -> hcLatencyBkt r == Excellent) results
    good      = length $ filter (\r -> hcLatencyBkt r == Good) results
    poor      = length $ filter (\r -> hcLatencyBkt r == Poor || hcLatencyBkt r == Unreachable) results
    avgLat    = if total > 0
                then sum (map hcLatencyMs results) / fromIntegral total
                else 0.0

    header  = "╔══════════════════════════════════════════════╗\n"
           ++ "║   CLASH IP CHECKER — HEALTH REPORT           ║\n"
           ++ "╠══════════════════════════════════════════════╣\n"

    summary = "║ Total proxies : " ++ show total ++ "\n"
           ++ "║ Reachable     : " ++ show reachable ++ "/" ++ show total ++ "\n"
           ++ "║ Excellent     : " ++ show excellent ++ "\n"
           ++ "║ Good          : " ++ show good ++ "\n"
           ++ "║ Poor/Down     : " ++ show poor ++ "\n"
           ++ "║ Avg latency   : " ++ show (round avgLat :: Int) ++ "ms\n"

    footer  = "╚══════════════════════════════════════════════╝"

  in header ++ summary ++ footer

-- ---- Utility ---------------------------------------------------------------

splitOn :: Char -> String -> [String]
splitOn _ [] = [""]
splitOn c s  = case break (== c) s of
  (w, [])    -> [w]
  (w, _:rest) -> w : splitOn c rest

readMaybe :: String -> Maybe Int
readMaybe s
  | all isDigit s && not (null s) = Just (read s)
  | otherwise = Nothing
