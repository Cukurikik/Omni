module Omni
  module Business
    module MlperfTrainingBench
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

      class BenchmarkRules
        def validate_convergence(target_accuracy, current_accuracy, elapsed_time_minutes)
          if target_accuracy <= 0.0 || target_accuracy > 1.0
            return OmniResult.new(error: StandardError.new("Target accuracy must be between 0.0 and 1.0"))
          end

          # MLPerf convergence rules
          # The run is considered successful if current_accuracy >= target_accuracy
          if current_accuracy >= target_accuracy
            return OmniResult.new(value: { 
              status: "CONVERGED", 
              time_to_train: elapsed_time_minutes,
              action: "STOP_TRAINING_AND_REPORT"
            })
          end

          if elapsed_time_minutes > 10000.0
            return OmniResult.new(value: {
              status: "TIMEOUT",
              reason: "Exceeded maximum allowed training time",
              action: "ABORT_RUN"
            })
          end

          OmniResult.new(value: { status: "TRAINING", action: "CONTINUE_EPOCH" })
        end
      end
    end
  end
end
