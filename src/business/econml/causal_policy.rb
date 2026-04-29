# OMNI Ruby Business Layer: EconML Causal Policy
# Domain rules that consume the Average Treatment Effect (ATE) and dictate business actions.

module Omni
  module Business
    module EconML
      
      class PolicyResult
        attr_reader :action, :confidence, :reason

        def initialize(action, confidence, reason)
          @action = action
          @confidence = confidence
          @reason = reason
        end
      end

      class CausalDecisionEngine
        # threshold = Minimum ATE magnitude to trigger a policy change
        def initialize(ate_threshold: 0.05, p_value_max: 0.01)
          @ate_threshold = ate_threshold
          @p_value_max = p_value_max
        end

        def evaluate_pricing_treatment(experiment_data)
          ate = experiment_data[:average_treatment_effect]
          p_value = experiment_data[:p_value] || 0.005 # Assume significance if absent

          if p_value > @p_value_max
            return PolicyResult.new(
              :maintain_status_quo, 
              0.0, 
              "Treatment effect is statistically insignificant (p > #{@p_value_max})"
            )
          end

          if ate > @ate_threshold
            PolicyResult.new(
              :rollout_treatment, 
              ate, 
              "Treatment significantly increases target metric by #{ate.round(4)}"
            )
          elsif ate < -@ate_threshold
            PolicyResult.new(
              :rollback_treatment, 
              ate.abs, 
              "Treatment causes significant degradation of target metric"
            )
          else
            PolicyResult.new(
              :monitor, 
              ate.abs, 
              "Treatment effect exists but is below rollout threshold (#{@ate_threshold})"
            )
          end
        end
      end

    end
  end
end
