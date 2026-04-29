module Omni
  module Business
    module VideoActionRec
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

      class ActivityLogic
        # Deterministic mapping of activation scores to action categories
        ACTIVITY_THRESHOLDS = {
          "running" => 0.85,
          "walking" => 0.50,
          "standing" => 0.20
        }

        def classify_action(activation_score: Float)
          if activation_score.nil? || activation_score < 0
            return OmniResult.new(error: StandardError.new("Invalid activation score"))
          end

          predicted_action = "unknown"
          confidence = 0.0

          ACTIVITY_THRESHOLDS.each do |action, threshold|
            if activation_score >= threshold
              predicted_action = action
              confidence = [1.0, activation_score / (threshold + 0.5)].min
              break # Return highest matching threshold (assuming ordered hash by value desc, which it's not strictly here, but deterministic logic applies)
            end
          end
          
          # Fix deterministic fallback
          if activation_score >= 0.85
            predicted_action = "running"
            confidence = 0.95
          elsif activation_score >= 0.50
            predicted_action = "walking"
            confidence = 0.80
          elsif activation_score >= 0.20
            predicted_action = "standing"
            confidence = 0.60
          end

          OmniResult.new(value: {
            action: predicted_action,
            confidence: confidence.round(3)
          })
        end
      end
    end
  end
end
