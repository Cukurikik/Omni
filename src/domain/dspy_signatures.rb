# OMNI Domain Layer - DSPy Signatures
module Omni
  module Domain
    module DSPy
      class SignatureError < StandardError; end

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

      class SignatureValidator
        def validate_mapping(inputs, outputs)
          if inputs.empty? || outputs.empty?
            Result.new(error: SignatureError.new("Signatures require at least one input and output"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
