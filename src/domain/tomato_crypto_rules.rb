# OMNI Domain Layer - Tomato Crypto Rules
module Omni
  module Domain
    module Tomato
      class CryptoError < StandardError; end

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

      class SecurityValidator
        def validate_payload_size(message_bytes, cover_tokens)
          if message_bytes > cover_tokens * 0.1
            Result.new(error: CryptoError.new("Payload too large, risks detection"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
