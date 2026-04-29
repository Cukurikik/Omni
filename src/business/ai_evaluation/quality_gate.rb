module Omni
  module Business
    module AIEvaluation
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

      class QualityGate
        def initialize(drift_threshold: 0.5)
          @threshold = drift_threshold
        end

        def evaluate_deployment_gate(drift_score: Float)
          if drift_score < 0
            return OmniResult.new(error: StandardError.new("Drift score cannot be negative"))
          end

          # Business rules for AI model deployment
          if drift_score > @threshold
            return OmniResult.new(value: { 
              decision: "REJECT", 
              reason: "Drift score #{drift_score} exceeds threshold #{@threshold}" 
            })
          end

          OmniResult.new(value: { 
            decision: "APPROVE", 
            reason: "Model within acceptable quality parameters" 
          })
        end
      end
    end
  end
end
