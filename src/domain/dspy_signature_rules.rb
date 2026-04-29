# OMNI Domain Layer - DSPy Signature Rules
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
        def validate_io_format(sig_string)
          if !sig_string.include?("->")
            Result.new(error: SignatureError.new("Signature must contain '->' separator"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
