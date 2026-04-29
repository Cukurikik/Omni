# OMNI Domain Layer - x1 Blueprint
module Omni
  module Domain
    module X1
      class BlueprintError < StandardError; end

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

      class PolicyValidator
        def validate_exploration(weight)
          if weight < 0.0 || weight > 5.0
            Result.new(error: BlueprintError.new("Exploration weight out of bounds"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
