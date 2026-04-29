module Omni
  module Business
    module Argon2Hasher
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

      class PasswordPolicy
        def validate_policy(password)
          if password.nil? || password.empty?
            return OmniResult.new(error: StandardError.new("Password cannot be empty"))
          end

          if password.length < 12
            return OmniResult.new(error: StandardError.new("Password must be at least 12 characters (OWASP Strict)"))
          end

          unless password.match?(/[A-Z]/)
            return OmniResult.new(error: StandardError.new("Password must contain uppercase letter"))
          end

          unless password.match?(/[0-9]/)
            return OmniResult.new(error: StandardError.new("Password must contain number"))
          end

          unless password.match?(/[^a-zA-Z0-9]/)
            return OmniResult.new(error: StandardError.new("Password must contain special character"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
