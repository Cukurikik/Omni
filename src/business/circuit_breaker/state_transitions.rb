module Omni
  module Business
    module CircuitBreaker
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

      class StateTransitions
        def evaluate_transition(current_state, current_error_rate, threshold, time_in_open_ms, reset_timeout_ms)
          # Strict Circuit Breaker State Machine Rules
          # States: CLOSED (Healthy), OPEN (Failing/Tripped), HALF_OPEN (Testing recovery)

          case current_state.upcase
          when "CLOSED"
            if current_error_rate >= threshold
              return OmniResult.new(value: "OPEN") # Trip breaker
            end
            OmniResult.new(value: "CLOSED")

          when "OPEN"
            if time_in_open_ms >= reset_timeout_ms
              return OmniResult.new(value: "HALF_OPEN") # Test recovery
            end
            OmniResult.new(value: "OPEN")

          when "HALF_OPEN"
            # In half-open, a single error trips it back to OPEN. 
            # If error rate is 0 (healthy), transition to CLOSED.
            if current_error_rate > 0.0
              return OmniResult.new(value: "OPEN")
            else
              return OmniResult.new(value: "CLOSED")
            end

          else
            OmniResult.new(error: StandardError.new("Invalid circuit breaker state"))
          end
        end
      end
    end
  end
end
