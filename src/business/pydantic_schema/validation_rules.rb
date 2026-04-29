module Omni
  module Business
    module PydanticSchema
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

      class ValidationRules
        def validate_string_constraints(value, min_length, max_length, pattern)
          if value.nil?
            return OmniResult.new(error: StandardError.new("String cannot be null"))
          end

          len = value.length

          if min_length && len < min_length
            return OmniResult.new(error: StandardError.new("String length #{len} is less than minimum #{min_length}"))
          end

          if max_length && len > max_length
            return OmniResult.new(error: StandardError.new("String length #{len} is greater than maximum #{max_length}"))
          end

          if pattern && !value.match?(Regexp.new(pattern))
            return OmniResult.new(error: StandardError.new("String does not match required regex pattern"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
