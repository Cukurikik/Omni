# OMNI Domain Layer - Custom Diffusion Concept Rules
module Omni
  module Domain
    module CustomDiffusion
      class ConceptError < StandardError; end

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

      class ConceptValidator
        def validate_concept_token(token)
          if token.nil? || token.length < 2 || !token.start_with?("<") || !token.end_with?(">")
            Result.new(error: ConceptError.new("Invalid concept token format. Must be like <concept>"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
