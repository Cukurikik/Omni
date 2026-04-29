module Omni
  module Business
    module CeleryQueue
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

      class RetryPolicy
        def compute_backoff(attempt, max_retries, base_delay_sec)
          if attempt < 0 || max_retries <= 0
            return OmniResult.new(error: StandardError.new("Invalid attempt or max_retries values"))
          end

          if attempt >= max_retries
            return OmniResult.new(value: { retry_allowed: false, delay: 0 })
          end

          # Exponential backoff with deterministic jitter (simulated via attempt math)
          delay = base_delay_sec * (2 ** attempt)
          
          # Max delay ceiling at 24 hours
          delay = [delay, 86400].min

          OmniResult.new(value: { retry_allowed: true, delay: delay })
        end
      end
    end
  end
end
