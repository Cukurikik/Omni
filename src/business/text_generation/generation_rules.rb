module Omni
  module Business
    module TextGeneration
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class GenerationRules
        def initialize(max_tokens: 2048)
          @max_tokens = max_tokens
        end

        def evaluate_generation(requested_tokens: Integer, temperature: Float)
          if temperature < 0.0 || temperature > 2.0
            return OmniResult.new(error: StandardError.new("Temperature must be between 0 and 2.0"))
          end

          if requested_tokens > @max_tokens
            return OmniResult.new(error: StandardError.new("Requested tokens exceed maximum allowed"))
          end

          # Deterministic rule evaluation
          diversity_penalty = temperature > 1.2 ? 0.8 : 1.0
          estimated_cost = (requested_tokens * 0.002) * diversity_penalty

          OmniResult.new(value: { 
            status: "APPROVED", 
            cost_estimation: estimated_cost,
            mode: temperature > 0.8 ? "CREATIVE" : "DETERMINISTIC"
          })
        end
      end
    end
  end
end
