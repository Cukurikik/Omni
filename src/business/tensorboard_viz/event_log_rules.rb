module Omni
  module Business
    module TensorboardViz
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

      class EventLogRules
        def validate_event_record(step, wall_time, tag, value_type)
          if step < 0
            return OmniResult.new(error: StandardError.new("Step must be non-negative"))
          end

          if wall_time <= 0
            return OmniResult.new(error: StandardError.new("Wall time must be strictly positive epoch timestamp"))
          end

          if tag.nil? || tag.strip.empty?
            return OmniResult.new(error: StandardError.new("Event tag cannot be empty"))
          end

          allowed_types = ["SCALAR", "HISTOGRAM", "IMAGE", "AUDIO", "TENSOR"]
          unless allowed_types.include?(value_type)
            return OmniResult.new(error: StandardError.new("Unsupported TensorBoard event value type: #{value_type}"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
