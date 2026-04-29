# OMNI Domain Layer - SRBench Rules
module Omni
  module Domain
    module SRBench
      class RuleError < StandardError; end

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

      class EquationValidator
        def validate_complexity(num_terms, max_allowed)
          if num_terms > max_allowed
            Result.new(error: RuleError.new("Equation too complex: #{num_terms} terms > #{max_allowed}"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
