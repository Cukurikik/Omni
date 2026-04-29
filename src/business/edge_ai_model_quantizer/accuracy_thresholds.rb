module Omni
  module Business
    module EdgeAiModelQuantizer
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

      class AccuracyThresholds
        def is_quantization_acceptable(fp32_accuracy_percent, int8_accuracy_percent, max_drop_percent)
          if max_drop_percent < 0 || fp32_accuracy_percent < 0 || int8_accuracy_percent < 0
            return OmniResult.new(error: StandardError.new("Percentages must be positive"))
          end

          # AI Business Logic: Quantization Accuracy Limits
          # Quantizing a model to INT8 always results in a slight loss of accuracy.
          # If the accuracy drop is too severe (e.g., object detection fails), we must abort
          # and fall back to FP16 or FP32, accepting slower inference.
          
          accuracy_drop = fp32_accuracy_percent - int8_accuracy_percent
          
          if accuracy_drop > max_drop_percent
             return OmniResult.new(value: { 
               acceptable: false, 
               reason: "ABORT: INT8 quantization caused a #{accuracy_drop}% accuracy drop, exceeding the #{max_drop_percent}% limit." 
             })
          end
          
          OmniResult.new(value: { acceptable: true, reason: "Model successfully compressed. Accuracy maintained." })
        end
      end
    end
  end
end
