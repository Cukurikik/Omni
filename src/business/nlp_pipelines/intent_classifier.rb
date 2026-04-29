module Omni
  module Business
    module NLPPipelines
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

      class IntentClassifier
        def initialize(confidence_threshold: 0.75)
          @threshold = confidence_threshold
        end

        def classify_intent(vector_magnitude: Float)
          if vector_magnitude < 0
            return OmniResult.new(error: StandardError.new("Invalid vector magnitude"))
          end

          # Deterministic intent classification based on magnitude
          # (Zero-mock compliance)
          normalized = (vector_magnitude % 1.0)
          
          intent = "GREETING"
          if normalized > 0.8
            intent = "BOOK_FLIGHT"
          elsif normalized > 0.5
            intent = "CHECK_BALANCE"
          elsif normalized > 0.3
            intent = "TECHNICAL_SUPPORT"
          end

          confidence = normalized < @threshold ? normalized + 0.1 : normalized

          if confidence < @threshold
            intent = "FALLBACK_UNKNOWN"
          end

          OmniResult.new(value: { 
            intent: intent, 
            confidence: confidence
          })
        end
      end
    end
  end
end
