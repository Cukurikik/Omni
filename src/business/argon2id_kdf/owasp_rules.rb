module Omni
  module Business
    module Argon2idKDF
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

      class OWASPRules
        def validate_parameters(m_cost, t_cost, p_cost)
          # Strict OWASP recommended minimums for Argon2id
          
          if m_cost < 19456 # 19 MB minimum memory
            return OmniResult.new(error: StandardError.new("Memory cost (m) must be at least 19 MiB for OWASP compliance"))
          end
          
          if t_cost < 2 # 2 iterations minimum
            return OmniResult.new(error: StandardError.new("Time cost (t) must be at least 2 iterations"))
          end
          
          if p_cost < 1 # Minimum 1 parallel lane
            return OmniResult.new(error: StandardError.new("Parallelism (p) must be at least 1"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
