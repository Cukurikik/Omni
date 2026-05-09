require 'base64'
require 'json'
require 'openssl'

module Omni
  module Domain
    module MoE
      # OMNI MOTHER Production Zero-Mock JWT Validator
      # Validates stateless tokens before accessing the Omni Router API
      
      class InvalidTokenError < StandardError; end

      class JwtValidator
        def initialize(public_key_pem)
          @public_key = OpenSSL::PKey::RSA.new(public_key_pem)
        end

        def decode_and_verify(token)
          parts = token.split('.')
          raise InvalidTokenError, "OMNI CRITICAL: Invalid JWT structure" unless parts.size == 3
          
          header_b64, payload_b64, sig_b64 = parts

          # 1. Verify Signature
          signing_input = "#{header_b64}.#{payload_b64}"
          signature = base64_url_decode(sig_b64)
          
          is_valid = @public_key.verify(OpenSSL::Digest::SHA256.new, signature, signing_input)
          raise InvalidTokenError, "OMNI CRITICAL: JWT Signature mismatch" unless is_valid

          # 2. Parse Payload
          payload = JSON.parse(base64_url_decode(payload_b64))

          # 3. Verify Expiration
          if payload['exp'] && Time.now.to_i > payload['exp']
            raise InvalidTokenError, "OMNI CRITICAL: JWT Token has expired"
          end

          payload
        end

        private

        def base64_url_decode(str)
          str += '=' * (4 - str.length % 4) if str.length % 4 != 0
          Base64.urlsafe_decode64(str)
        end
      end
    end
  end
end
