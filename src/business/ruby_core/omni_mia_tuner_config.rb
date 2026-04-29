# Omni MIA-Tuner Knowledge Distill (Ruby)
# Business Layer: Multi-image adaptation tuning configuration.
# Ref: tsinghua-fib-lab/AAAI2025_MIA-Tuner — AAAI 2025.
module Omni
  module MIATuner
    Config = Struct.new(:base_model, :adapter_rank, :learning_rate, :images_per_concept, keyword_init: true)
    def self.validate_config(cfg)
      return { error: 'Rank must be > 0' } if cfg.adapter_rank <= 0
      return { error: 'LR must be positive' } if cfg.learning_rate <= 0
      { status: :valid, scaling: (cfg.adapter_rank * cfg.learning_rate).round(8) }
    end
  end
end
