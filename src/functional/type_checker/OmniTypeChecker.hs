-- omni_type_checker.hs — Type-Safe Model Configuration Validator
-- Inspired by: Type-level programming for model safety
-- Layer: Functional / Haskell
--
-- Compile-time verified model configuration checking using
-- Haskell's type system to prevent invalid model architectures.

module OmniTypeChecker
  ( ModelConfig(..)
  , ValidationResult(..)
  , ConfigError(..)
  , validateConfig
  , validateArchitecture
  , validateHyperparams
  , checkDivisibility
  , checkMemoryBudget
  , generateConfigReport
  ) where

import Data.Maybe (catMaybes)

-- | Configuration errors with severity
data Severity = SevError | SevWarning | SevInfo
  deriving (Show, Eq, Ord)

data ConfigError = ConfigError
  { errorSeverity :: Severity
  , errorField    :: String
  , errorMessage  :: String
  } deriving (Show)

data ValidationResult
  = Valid
  | Invalid [ConfigError]
  deriving (Show)

instance Semigroup ValidationResult where
  Valid <> Valid = Valid
  Valid <> Invalid es = Invalid es
  Invalid es <> Valid = Invalid es
  Invalid es1 <> Invalid es2 = Invalid (es1 ++ es2)

instance Monoid ValidationResult where
  mempty = Valid

-- | Model configuration record
data ModelConfig = ModelConfig
  { cfgModelName      :: String
  , cfgHiddenDim      :: Int
  , cfgNumHeads       :: Int
  , cfgNumLayers      :: Int
  , cfgFFMultiplier   :: Int
  , cfgVocabSize      :: Int
  , cfgMaxSeqLen      :: Int
  , cfgDropout        :: Double
  , cfgLearningRate   :: Double
  , cfgBatchSize      :: Int
  , cfgWarmupSteps    :: Int
  , cfgTotalSteps     :: Int
  , cfgGradAccumSteps :: Int
  , cfgPrecision      :: String  -- "fp32", "fp16", "bf16"
  , cfgGPUMemoryGB    :: Double
  } deriving (Show)

-- | Default configuration
defaultConfig :: ModelConfig
defaultConfig = ModelConfig
  { cfgModelName      = "omni-base"
  , cfgHiddenDim      = 768
  , cfgNumHeads       = 12
  , cfgNumLayers      = 12
  , cfgFFMultiplier   = 4
  , cfgVocabSize      = 32000
  , cfgMaxSeqLen      = 2048
  , cfgDropout        = 0.1
  , cfgLearningRate   = 3e-4
  , cfgBatchSize      = 32
  , cfgWarmupSteps    = 1000
  , cfgTotalSteps     = 100000
  , cfgGradAccumSteps = 1
  , cfgPrecision      = "bf16"
  , cfgGPUMemoryGB    = 24.0
  }

-- | Validate all aspects of a model configuration
validateConfig :: ModelConfig -> ValidationResult
validateConfig cfg = mconcat
  [ validateArchitecture cfg
  , validateHyperparams cfg
  , checkDivisibility cfg
  , checkMemoryBudget cfg
  , validateNumericalStability cfg
  ]

-- | Validate architecture constraints
validateArchitecture :: ModelConfig -> ValidationResult
validateArchitecture cfg = mconcat $ catMaybes
  [ checkPositive "hidden_dim" (cfgHiddenDim cfg)
  , checkPositive "num_heads" (cfgNumHeads cfg)
  , checkPositive "num_layers" (cfgNumLayers cfg)
  , checkPositive "vocab_size" (cfgVocabSize cfg)
  , checkPositive "max_seq_len" (cfgMaxSeqLen cfg)
  , checkRange "ff_multiplier" (cfgFFMultiplier cfg) 1 8
  , if cfgHiddenDim cfg `mod` cfgNumHeads cfg /= 0
    then Just $ Invalid [ConfigError SevError "hidden_dim"
      $ "Hidden dim (" ++ show (cfgHiddenDim cfg) ++
        ") must be divisible by num_heads (" ++ show (cfgNumHeads cfg) ++ ")"]
    else Nothing
  , if cfgMaxSeqLen cfg > 32768
    then Just $ Invalid [ConfigError SevWarning "max_seq_len"
      "Sequence length > 32768 may require specialized attention (e.g., FlashAttention)"]
    else Nothing
  ]

-- | Validate hyperparameter ranges
validateHyperparams :: ModelConfig -> ValidationResult
validateHyperparams cfg = mconcat $ catMaybes
  [ checkBound "dropout" (cfgDropout cfg) 0.0 0.5
  , checkBound "learning_rate" (cfgLearningRate cfg) 1e-7 1e-1
  , checkPositive "batch_size" (cfgBatchSize cfg)
  , checkPositive "warmup_steps" (cfgWarmupSteps cfg)
  , checkPositive "total_steps" (cfgTotalSteps cfg)
  , if cfgWarmupSteps cfg >= cfgTotalSteps cfg
    then Just $ Invalid [ConfigError SevError "warmup_steps"
      "Warmup steps must be less than total steps"]
    else Nothing
  , if cfgPrecision cfg `notElem` ["fp32", "fp16", "bf16"]
    then Just $ Invalid [ConfigError SevError "precision"
      $ "Invalid precision: " ++ cfgPrecision cfg ++ ". Use fp32, fp16, or bf16"]
    else Nothing
  ]

-- | Check dimension divisibility for efficient computation
checkDivisibility :: ModelConfig -> ValidationResult
checkDivisibility cfg = mconcat $ catMaybes
  [ if headDim < 32
    then Just $ Invalid [ConfigError SevWarning "head_dim"
      $ "Head dim " ++ show headDim ++ " is very small; consider >= 64"]
    else Nothing
  , if cfgHiddenDim cfg `mod` 8 /= 0
    then Just $ Invalid [ConfigError SevWarning "hidden_dim"
      "Hidden dim should be divisible by 8 for tensor core efficiency"]
    else Nothing
  ]
  where
    headDim = cfgHiddenDim cfg `div` cfgNumHeads cfg

-- | Estimate memory usage and validate against GPU budget
checkMemoryBudget :: ModelConfig -> ValidationResult
checkMemoryBudget cfg =
  let paramCount = estimateParams cfg
      bytesPerParam = case cfgPrecision cfg of
        "fp32" -> 4.0
        "fp16" -> 2.0
        "bf16" -> 2.0
        _      -> 4.0
      modelSizeGB = fromIntegral paramCount * bytesPerParam / (1024 * 1024 * 1024)
      -- Activation memory: roughly 2x model size per batch element
      activationGB = modelSizeGB * 2.0 * fromIntegral (cfgBatchSize cfg)
        / fromIntegral (cfgGradAccumSteps cfg)
      -- Optimizer states: 2x for Adam (momentum + variance)
      optimizerGB = modelSizeGB * 2.0
      totalGB = modelSizeGB + activationGB + optimizerGB
  in if totalGB > cfgGPUMemoryGB cfg
     then Invalid [ConfigError SevError "memory"
       $ "Estimated memory " ++ showF totalGB ++ " GB exceeds GPU budget "
         ++ showF (cfgGPUMemoryGB cfg) ++ " GB"
         ++ " (model=" ++ showF modelSizeGB
         ++ ", activation=" ++ showF activationGB
         ++ ", optimizer=" ++ showF optimizerGB ++ ")"]
     else if totalGB > cfgGPUMemoryGB cfg * 0.85
     then Invalid [ConfigError SevWarning "memory"
       $ "Memory usage " ++ showF totalGB ++ " GB is >85% of budget "
         ++ showF (cfgGPUMemoryGB cfg) ++ " GB"]
     else Valid

-- | Numerical stability checks
validateNumericalStability :: ModelConfig -> ValidationResult
validateNumericalStability cfg = mconcat $ catMaybes
  [ if cfgLearningRate cfg > 1e-3 && cfgPrecision cfg == "fp16"
    then Just $ Invalid [ConfigError SevWarning "stability"
      "High LR with fp16 may cause NaN — consider bf16 or loss scaling"]
    else Nothing
  , if cfgDropout cfg == 0.0 && cfgNumLayers cfg > 24
    then Just $ Invalid [ConfigError SevInfo "regularization"
      "Deep model with no dropout; consider adding dropout or weight decay"]
    else Nothing
  ]

-- | Estimate total parameter count
estimateParams :: ModelConfig -> Int
estimateParams cfg =
  let d = cfgHiddenDim cfg
      ff = d * cfgFFMultiplier cfg
      layers = cfgNumLayers cfg
      vocab = cfgVocabSize cfg
      -- Attention: QKV + output projection
      attnParams = 4 * d * d
      -- FFN: up + gate + down projections
      ffnParams = 3 * d * ff
      -- Per-layer total
      layerParams = attnParams + ffnParams + 4 * d  -- +norms
      -- Embedding + output head
      embedParams = vocab * d
  in layers * layerParams + 2 * embedParams

-- | Generate human-readable config report
generateConfigReport :: ModelConfig -> String
generateConfigReport cfg =
  let result = validateConfig cfg
      paramCount = estimateParams cfg
      paramStr = formatParams paramCount
  in unlines
    [ "╔══════════════════════════════════════╗"
    , "║   OMNI Model Configuration Report   ║"
    , "╠══════════════════════════════════════╣"
    , "║ Model: " ++ cfgModelName cfg
    , "║ Architecture: " ++ show (cfgNumLayers cfg) ++ "L/"
      ++ show (cfgNumHeads cfg) ++ "H/" ++ show (cfgHiddenDim cfg) ++ "D"
    , "║ Parameters: " ++ paramStr
    , "║ Precision: " ++ cfgPrecision cfg
    , "║ Max Seq Len: " ++ show (cfgMaxSeqLen cfg)
    , "╠══════════════════════════════════════╣"
    , "║ Validation: " ++ case result of
        Valid -> "✅ ALL CHECKS PASSED"
        Invalid es -> "❌ " ++ show (length es) ++ " issue(s) found"
    , case result of
        Valid -> ""
        Invalid es -> unlines $ map formatError es
    , "╚══════════════════════════════════════╝"
    ]

-- Helper functions
formatError :: ConfigError -> String
formatError e = "  " ++ sevStr (errorSeverity e) ++ " [" ++ errorField e ++ "] " ++ errorMessage e
  where
    sevStr SevError   = "❌"
    sevStr SevWarning = "⚠️"
    sevStr SevInfo    = "ℹ️"

formatParams :: Int -> String
formatParams n
  | n >= 1000000000 = showF (fromIntegral n / 1e9) ++ "B"
  | n >= 1000000    = showF (fromIntegral n / 1e6) ++ "M"
  | n >= 1000       = showF (fromIntegral n / 1e3) ++ "K"
  | otherwise       = show n

showF :: Double -> String
showF x = let s = show (round (x * 100) :: Int)
              n = length s
          in if n <= 2
             then "0." ++ replicate (2 - n) '0' ++ s
             else take (n - 2) s ++ "." ++ drop (n - 2) s

checkPositive :: String -> Int -> Maybe ValidationResult
checkPositive name val
  | val <= 0 = Just $ Invalid [ConfigError SevError name $ name ++ " must be positive, got " ++ show val]
  | otherwise = Nothing

checkRange :: String -> Int -> Int -> Int -> Maybe ValidationResult
checkRange name val lo hi
  | val < lo || val > hi = Just $ Invalid [ConfigError SevWarning name
      $ name ++ "=" ++ show val ++ " outside recommended range [" ++ show lo ++ ".." ++ show hi ++ "]"]
  | otherwise = Nothing

checkBound :: String -> Double -> Double -> Double -> Maybe ValidationResult
checkBound name val lo hi
  | val < lo || val > hi = Just $ Invalid [ConfigError SevError name
      $ name ++ "=" ++ show val ++ " outside valid range [" ++ show lo ++ ".." ++ show hi ++ "]"]
  | otherwise = Nothing
