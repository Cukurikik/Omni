module Omni
  module Business
    module TimeLLM

      class OmniResult
        attr_reader :data, :error
        def initialize(data: nil, error: nil)
          @data = data
          @error = error
        end
        def ok?
          @error.nil?
        end
      end

      class ForecastEvaluator
        def initialize(threshold_mse: 0.05)
          @threshold_mse = threshold_mse
        end

        def evaluate_prediction(ground_truth, forecast)
          return OmniResult.new(error: "Inputs cannot be nil") if ground_truth.nil? || forecast.nil?
          return OmniResult.new(error: "Length mismatch") if ground_truth.length != forecast.length
          return OmniResult.new(error: "Empty arrays") if ground_truth.empty?
          
          # Mathematical MSE Calculation
          squared_errors = ground_truth.zip(forecast).map do |gt, fc|
            (gt - fc) ** 2
          end
          
          mse = squared_errors.sum / squared_errors.length.to_f
          
          is_valid = mse <= @threshold_mse
          
          OmniResult.new(data: {
            mse: mse,
            is_valid: is_valid,
            action: is_valid ? "commit_to_db" : "flag_for_retraining"
          })
        end
      end

    end
  end
end
