# OMNI Domain Layer - JAX Array Shape Rules
module Omni
  module Domain
    module JAX
      class ShapeError < StandardError; end

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

      class ArrayValidator
        def validate_broadcastable(shape_a, shape_b)
          # Abstract numpy broadcasting rule check
          if shape_a.empty? || shape_b.empty?
            Result.new(error: ShapeError.new("Empty shapes cannot be broadcast"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
