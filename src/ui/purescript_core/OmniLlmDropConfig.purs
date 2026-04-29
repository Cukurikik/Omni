-- Omni LLM-Drop Config (PureScript)
-- Interface Layer: Purely functional configuration generator for layer dropping.

module Omni.LlmDropConfig where

import Prelude

type DropConfig = {
  modelName :: String,
  dropRate :: Number,
  isDeterministic :: Boolean
}

generateStrictConfig :: String -> Number -> DropConfig
generateStrictConfig name rate =
  let
    boundedRate = if rate < 0.0 then 0.0 else if rate > 1.0 then 1.0 else rate
  in
    { modelName: name, dropRate: boundedRate, isDeterministic: true }

defaultConfig :: DropConfig
defaultConfig = generateStrictConfig "Omni-Transformer-Base" 0.2
