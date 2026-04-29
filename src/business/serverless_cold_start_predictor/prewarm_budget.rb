module Omni
  module Business
    module ServerlessColdStartPredictor
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

      class PrewarmBudget
        def should_prewarm(probability_of_invocation, function_tier)
          if probability_of_invocation < 0.0 || probability_of_invocation > 1.0
            return OmniResult.new(error: StandardError.new("Probability must be between 0.0 and 1.0"))
          end

          # Cold-Start Business Logic: Pre-warming Budget Constraints
          # Pre-warming AWS Lambdas or Firecracker VMs costs money. We only do it if statistically justified.
          
          threshold = case function_tier
          when "MISSION_CRITICAL"
             0.05 # Pre-warm if there's even a 5% chance of invocation
          when "STANDARD"
             0.40 # Pre-warm at 40% probability
          when "BATCH_JOB"
             0.95 # Rarely pre-warm background jobs
          else
             1.00 # Never pre-warm unknown
          end
          
          if probability_of_invocation >= threshold
             return OmniResult.new(value: { prewarm: true })
          end
          
          OmniResult.new(value: { prewarm: false })
        end
      end
    end
  end
end
