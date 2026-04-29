# Omni PairCoder Workflow Config (Ruby)
# Ref: nju-websoft/PairCoder — ASE'24
module Omni
  module PairCoderConfig
    STRATEGIES = %w[divide_and_conquer brute_force greedy dynamic_programming].freeze
    PlanConfig = Struct.new(:strategy, :max_plans, :refinement_rounds, keyword_init: true)
    def self.validate(cfg)
      return { error: 'Invalid strategy' } unless STRATEGIES.include?(cfg.strategy)
      return { error: 'Plans must be >= 1' } if cfg.max_plans < 1
      { status: :valid, config: cfg }
    end
  end
end
