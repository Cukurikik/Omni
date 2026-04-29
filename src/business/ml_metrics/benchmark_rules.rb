module Omni
  module Business
    module MLMetrics
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
        def initialize(target_accuracy: 0.90)
          @target_accuracy = target_accuracy
        end

        def check_compliance(current_accuracy: Float)
          if current_accuracy < 0.0 || current_accuracy > 1.0
            return OmniResult.new(error: StandardError.new("Accuracy out of bounds"))
          end

          if current_accuracy >= @target_accuracy
            OmniResult.new(value: "PASS_DEPLOY")
          elsif current_accuracy >= @target_accuracy - 0.05
            OmniResult.new(value: "WARN_REVIEW")
          else
            OmniResult.new(value: "FAIL_REJECT")
          end
        end
      end
    end
  end
end
