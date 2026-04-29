# Omni Deliberative Prompting Config (Ruby)
# Business: Deliberative reasoning prompt configuration.
# Ref: logikon-ai/awesome-deliberative-prompting
module Omni
  module DeliberativePrompt
    Config = Struct.new(:strategy, :max_steps, :temperature, keyword_init: true)
    STRATEGIES = %w[chain_of_thought tree_of_thought self_consistency debate reflection].freeze
    def self.validate(cfg)
      return { error: 'Invalid strategy' } unless STRATEGIES.include?(cfg.strategy)
      return { error: 'Steps must be positive' } if cfg.max_steps <= 0
      { status: :valid, effective_temp: [cfg.temperature, 2.0].min }
    end
  end
end
