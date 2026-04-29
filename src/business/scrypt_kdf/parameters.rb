module Omni
  module Business
    module ScryptKDF
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

      class Parameters
        def validate_scrypt_params(n, r, p)
          # Strict parameter bounds checking for scrypt
          # N: CPU/Memory cost, r: block size, p: parallelization

          unless (n & (n - 1)) == 0 && n > 1
            return OmniResult.new(error: StandardError.new("N must be a power of 2 greater than 1"))
          end

          if r <= 0 || p <= 0
            return OmniResult.new(error: StandardError.new("r and p must be strictly positive"))
          end

          # RFC 7914 limits: r * p < 2^30
          if r * p >= (1 << 30)
            return OmniResult.new(error: StandardError.new("r * p is too large, violates RFC 7914 limit"))
          end

          # Business rule: Enforce minimum security (e.g., N >= 16384 for interactive logins)
          if n < 16384
            return OmniResult.new(error: StandardError.new("N is too low for modern security standards (minimum 16384)"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
