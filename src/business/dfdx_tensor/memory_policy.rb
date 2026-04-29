module Omni
  module Business
    module DFDXTensor
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

      class MemoryPolicy
        def initialize(max_tensor_bytes: 1_000_000_000) # 1GB
          @max_tensor_bytes = max_tensor_bytes
        end

        def validate_allocation(shape, dtype_size_bytes)
          if shape.nil? || shape.empty?
            return OmniResult.new(error: StandardError.new("Shape cannot be empty"))
          end

          if dtype_size_bytes <= 0
            return OmniResult.new(error: StandardError.new("DType size must be strictly positive"))
          end

          # Determine total elements
          total_elements = shape.reduce(1, :*)
          
          if total_elements <= 0
            return OmniResult.new(error: StandardError.new("Total elements must be strictly positive"))
          end

          total_bytes = total_elements * dtype_size_bytes

          # Enforce business rule strictly
          if total_bytes > @max_tensor_bytes
            return OmniResult.new(error: StandardError.new("Memory limit exceeded. Requested: #{total_bytes} bytes, Limit: #{@max_tensor_bytes} bytes."))
          end

          OmniResult.new(value: { allowed: true, bytes: total_bytes })
        end
      end
    end
  end
end
