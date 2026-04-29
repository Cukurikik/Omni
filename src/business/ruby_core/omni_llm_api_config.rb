# Omni LLM API Starterkit Config (Ruby)
# Ref: tleers/llm-api-starterkit
module Omni
  module LLMApiConfig
    EndpointConfig = Struct.new(:model, :max_tokens, :temperature, :stream, keyword_init: true)
    def self.validate(cfg)
      return { error: 'Missing model' } unless cfg.model
      return { error: 'Temperature out of range' } unless (0..2).include?(cfg.temperature || 0.7)
      { status: :valid, config: cfg }
    end
  end
end
