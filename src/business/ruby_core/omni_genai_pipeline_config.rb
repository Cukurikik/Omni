# Omni GenAIBook Pipeline Config (Ruby)
# Business Layer: Generative AI pipeline configuration.
# Ref: bahree/GenAIBook
module Omni
  module GenAIPipeline
    Config = Struct.new(:model, :temperature, :max_tokens, :provider, keyword_init: true)
    def self.validate(cfg)
      return { error: 'Model required' } if cfg.model.nil? || cfg.model.empty?
      return { error: 'Temperature out of range' } if cfg.temperature < 0 || cfg.temperature > 2
      { status: :valid, effective_tokens: [cfg.max_tokens, 4096].min }
    end
  end
end
