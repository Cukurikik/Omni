module Omni
  module Business
    module GrpcChannel
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

      class DeadlineRules
        def evaluate_deadline(client_timeout_ms, network_latency_ms)
          if client_timeout_ms <= 0
            return OmniResult.new(error: StandardError.new("Timeout must be strictly positive"))
          end

          # Business rule: If network latency exceeds the client deadline, drop the RPC early
          if network_latency_ms >= client_timeout_ms
            return OmniResult.new(value: { drop: true, reason: "DEADLINE_EXCEEDED" })
          end

          # Effective remaining time
          remaining = client_timeout_ms - network_latency_ms
          
          OmniResult.new(value: { drop: false, remaining_ms: remaining })
        end
      end
    end
  end
end
