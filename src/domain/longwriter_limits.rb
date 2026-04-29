# OMNI Domain Layer - LongWriter Limits
module Omni
  module Domain
    module LongWriter
      class LimitError < StandardError; end

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

      class ContextValidator
        def validate_generation_length(tokens)
          if tokens > 100_000
            Result.new(error: LimitError.new("Exceeds LongWriter 100k token limit"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
