module Omni
  module Business
    module PrivacyML

      class OmniResult
        attr_reader :data, :error
        def initialize(data: nil, error: nil)
          @data = data
          @error = error
        end
        def ok?
          @error.nil?
        end
      end

      class PrivacyPolicyEngine
        def initialize
          @policies = {
            "healthcare" => { min_epsilon: 0.1, allowed_aggregation: "homomorphic" },
            "finance" => { min_epsilon: 0.5, allowed_aggregation: "secure_mpc" },
            "public" => { min_epsilon: 10.0, allowed_aggregation: "plaintext" }
          }
        end

        def validate_aggregation_request(domain, epsilon, method)
          return OmniResult.new(error: "Unknown domain: #{domain}") unless @policies.key?(domain)
          
          policy = @policies[domain]
          
          if epsilon < policy[:min_epsilon]
            return OmniResult.new(error: "Epsilon #{epsilon} is too small for domain #{domain}. Minimum is #{policy[:min_epsilon]}.")
          end
          
          if method != policy[:allowed_aggregation]
            return OmniResult.new(error: "Method #{method} not permitted. Required: #{policy[:allowed_aggregation]}")
          end
          
          # Compute deterministic cryptographic clearance token
          clearance_token = Digest::SHA256.hexdigest("#{domain}-#{epsilon}-#{method}-#{Time.now.to_i / 3600}")
          
          OmniResult.new(data: { status: "approved", token: clearance_token })
        end
      end

    end
  end
end
