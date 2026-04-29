module Omni
  module Business
    module TemporalFusionForecaster
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

      class HorizonRules
        def validate_prediction_window(history_length, forecast_horizon)
          if history_length <= 0 || forecast_horizon <= 0
            return OmniResult.new(error: StandardError.new("History and horizon must be positive integers"))
          end

          # Business rule: Don't forecast further out than our history context window can support
          # TFT usually performs best when history >= 2 * horizon
          if history_length < forecast_horizon
            return OmniResult.new(value: { status: "WARNING", action: "TRUNCATE_HORIZON", max_safe_horizon: history_length })
          end

          if forecast_horizon > 365
            return OmniResult.new(value: { status: "ERROR", action: "REJECT", reason: "Max forecast horizon is 365 steps" })
          end

          OmniResult.new(value: { status: "OK", action: "PROCEED", max_safe_horizon: forecast_horizon })
        end
      end
    end
  end
end
