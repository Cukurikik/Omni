module Omni
  module Business
    module TinyLlmQuantizer
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

      class PerplexityLimits
        def is_quantization_acceptable(original_perplexity, quantized_perplexity)
          if original_perplexity <= 0.0 || quantized_perplexity <= 0.0
            return OmniResult.new(error: StandardError.new("Perplexity must be positive"))
          end

          # Quantizer Business Logic: Model Degradation Limits
          # Quantization saves memory but degrades intelligence. Ensure the model isn't "lobotomized".
          
          # If perplexity spikes by more than 15%, the INT4 quantization caused too much damage
          degradation_ratio = (quantized_perplexity - original_perplexity) / original_perplexity
          
          if degradation_ratio > 0.15
             return OmniResult.new(value: { acceptable: false, reason: "Perplexity degradation exceeds 15% limit" })
          end
          
          OmniResult.new(value: { acceptable: true, reason: "Quantization fidelity is within acceptable bounds" })
        end
      end
    end
  end
end
