module Omni
  module Business
    module AlibiDetect
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

      class AlertingThresholds
        def validate_drift_alert(ks_statistic, threshold, p_value, alpha_level)
          if threshold <= 0.0 || threshold >= 1.0
            return OmniResult.new(error: StandardError.new("KS threshold must be strictly between 0 and 1"))
          end

          if alpha_level <= 0.0 || alpha_level >= 1.0
            return OmniResult.new(error: StandardError.new("Alpha significance level must be strictly between 0 and 1"))
          end

          # Business logic: Alert if both distance exceeds threshold AND statistically significant
          is_drifted = (ks_statistic > threshold) && (p_value < alpha_level)

          OmniResult.new(value: { trigger_alert: is_drifted, severity: is_drifted ? "HIGH" : "NORMAL" })
        end
      end
    end
  end
end
