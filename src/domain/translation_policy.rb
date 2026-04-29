# OMNI Domain Layer - Translation Policy
module Omni
  module Domain
    module TRagx
      class PolicyError < StandardError; end

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

      class QualityValidator
        def validate_bleu_score(score)
          if score < 0.0 || score > 100.0
            Result.new(error: PolicyError.new("BLEU score must be between 0 and 100"))
          elsif score < 15.0
            Result.new(error: PolicyError.new("Translation quality critically low"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
