module Omni
  module Business
    module GossipProtocol
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

      class QuarantineRules
        def evaluate_suspicion(missed_pings, suspicion_threshold)
          if suspicion_threshold <= 0
            return OmniResult.new(error: StandardError.new("Suspicion threshold must be positive"))
          end

          # Gossip / SWIM Protocol business rules
          if missed_pings == 0
            return OmniResult.new(value: { state: "ALIVE", quarantine: false })
          end

          if missed_pings < suspicion_threshold
            return OmniResult.new(value: { state: "SUSPECT", quarantine: false })
          end

          # Node is considered dead/partitioned
          OmniResult.new(value: { state: "DEAD", quarantine: true })
        end
      end
    end
  end
end
