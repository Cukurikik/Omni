module Omni
  module Business
    module MolecularMPNN
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

      class ToxicityRules
        def initialize(toxicity_threshold: 0.85)
          @threshold = toxicity_threshold
        end

        def evaluate_molecule(predicted_toxicity: Float)
          if predicted_toxicity < 0.0 || predicted_toxicity > 1.0
            return OmniResult.new(error: StandardError.new("Toxicity score must be between 0 and 1"))
          end

          # Determine classification based on threshold
          classification = predicted_toxicity >= @threshold ? "TOXIC" : "SAFE"
          
          action = classification == "TOXIC" ? "REJECT_SYNTHESIS" : "PROCEED_TO_TRIALS"

          OmniResult.new(value: { 
            classification: classification,
            confidence: (1.0 - predicted_toxicity).abs,
            recommended_action: action
          })
        end
      end
    end
  end
end
