# OMNI Domain Layer - NeMo Curator Pipeline Spec
module Omni
  module Domain
    module NeMoCurator
      class PipelineError < StandardError; end

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

      class FilterValidator
        def validate_heuristic_filter(threshold)
          if threshold < 0.0 || threshold > 1.0
            Result.new(error: PipelineError.new("Threshold must be between 0 and 1"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
