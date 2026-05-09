-- OmniCoreTypes.hs — Core Configuration Data Types
-- Layer: Functional / Haskell
--
-- Purely functional data definitions for defining strict, algebraic
-- structures representing AI model parameters and infrastructure topologies.

module OmniCoreTypes where

-- | Supported Model Architectures
data Architecture 
    = TransformerEncoder
    | TransformerDecoder
    | MoE (Int) -- Number of experts
    | Mamba
    | Convolutional
    deriving (Show, Eq)

-- | Computation Precision
data Precision 
    = FP32
    | FP16
    | BF16
    | INT8
    | INT4
    deriving (Show, Eq, Ord)

-- | Model Configuration Record
data ModelConfig = ModelConfig
    { modelName    :: String
    , architecture :: Architecture
    , hiddenSize   :: Int
    , numLayers    :: Int
    , precision    :: Precision
    } deriving (Show, Eq)

-- | Deployment Environment
data Environment 
    = Development
    | Staging
    | Production
    | Edge (String) -- Edge region
    deriving (Show, Eq)

-- | Pure function to evaluate VRAM requirements based on pure math
estimateVRAM :: ModelConfig -> Float
estimateVRAM cfg =
    let baseParams = fromIntegral (hiddenSize cfg * hiddenSize cfg * numLayers cfg * 12)
        bytesPerParam = case precision cfg of
            FP32 -> 4.0
            FP16 -> 2.0
            BF16 -> 2.0
            INT8 -> 1.0
            INT4 -> 0.5
        -- Very rough estimation in Gigabytes
        gb = (baseParams * bytesPerParam) / (1024 * 1024 * 1024)
    in gb * 1.2 -- 20% overhead for KV Cache and Activations

-- | Smart constructor for ModelConfig ensuring validity
createConfig :: String -> Architecture -> Int -> Int -> Precision -> Either String ModelConfig
createConfig name arch hs layers prec
    | hs <= 0 = Left "Hidden size must be positive"
    | layers <= 0 = Left "Number of layers must be positive"
    | otherwise = Right $ ModelConfig name arch hs layers prec
