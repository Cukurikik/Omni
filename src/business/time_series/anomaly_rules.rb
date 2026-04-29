module Omni
  module Business
    module TimeSeries
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

      class AnomalyRules
        def initialize(std_dev_multiplier: 3.0)
          @threshold_multiplier = std_dev_multiplier
        end

        def evaluate_anomaly(value: Float, rolling_mean: Float, rolling_std: Float)
          if rolling_std < 0
            return OmniResult.new(error: StandardError.new("Standard deviation cannot be negative"))
          end

          # Business logic: Alert if value breaches rolling Z-score threshold
          z_score = rolling_std == 0.0 ? 0.0 : ((value - rolling_mean) / rolling_std).abs
          
          is_anomaly = z_score > @threshold_multiplier

          OmniResult.new(value: { 
            is_anomaly: is_anomaly,
            severity: is_anomaly ? (z_score > (@threshold_multiplier * 1.5) ? "CRITICAL" : "WARNING") : "NORMAL",
            z_score: z_score.round(4)
          })
        end
      end
    end
  end
end
