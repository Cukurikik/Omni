# OMNI Domain Layer - LightGBM Hyper Rules
module Omni
  module Domain
    module LightGBM
      class HyperError < StandardError; end

      class Result
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class Validator
        def validate_leaves_depth(num_leaves, max_depth)
          # LightGBM is leaf-wise, num_leaves shouldn't exceed 2^max_depth
          if max_depth > 0 && num_leaves > (2 ** max_depth)
            Result.new(error: HyperError.new("num_leaves cannot be larger than 2^max_depth"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
