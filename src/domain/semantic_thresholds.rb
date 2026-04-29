# OMNI Domain Layer - Semantic Thresholds
module Omni
  module Domain
    module SemanticRouter
      class ThresholdError < StandardError; end

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

      class RouteValidator
        def validate_confidence(score, threshold)
          if score < threshold
            Result.new(error: ThresholdError.new("Confidence score below semantic threshold"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
