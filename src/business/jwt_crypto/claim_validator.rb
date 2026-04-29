module Omni
  module Business
    module JWTCrypto
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class ClaimValidator
        def validate_claims(claims, current_time_sec)
          if claims.nil? || !claims.is_a?(Hash)
            return OmniResult.new(error: StandardError.new("Claims payload must be a valid JSON object"))
          end

          # Expiration Check (exp)
          if claims.key?('exp')
            if claims['exp'] < current_time_sec
              return OmniResult.new(error: StandardError.new("Token has expired"))
            end
          end

          # Not Before Check (nbf)
          if claims.key?('nbf')
            if claims['nbf'] > current_time_sec
              return OmniResult.new(error: StandardError.new("Token is not yet valid (nbf)"))
            end
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
