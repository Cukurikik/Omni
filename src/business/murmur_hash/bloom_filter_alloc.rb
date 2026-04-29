module Omni
  module Business
    module MurmurHash
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

      class BloomFilterAlloc
        def calculate_optimal_k(expected_elements, bit_array_size)
          if expected_elements <= 0 || bit_array_size <= 0
            return OmniResult.new(error: StandardError.new("Elements and array size must be positive"))
          end

          # Optimal number of hash functions: k = (m/n) * ln(2)
          # Where m is bit_array_size and n is expected_elements
          
          k_float = (bit_array_size.to_f / expected_elements) * Math.log(2)
          k_optimal = [k_float.round, 1].max # Minimum 1 hash function

          OmniResult.new(value: k_optimal)
        end
      end
    end
  end
end
