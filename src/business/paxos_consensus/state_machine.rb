module Omni
  module Business
    module PaxosConsensus
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

      class StateMachine
        def validate_proposal(current_round, proposal_round)
          if current_round < 0 || proposal_round < 0
            return OmniResult.new(error: StandardError.new("Rounds must be non-negative"))
          end

          # Paxos strict business rule: Acceptors only promise to rounds strictly greater than
          # the highest round they have seen so far.
          if proposal_round <= current_round
            return OmniResult.new(value: { accept: false, reason: "PROPOSAL_TOO_OLD" })
          end

          OmniResult.new(value: { accept: true, reason: "PROMISE_GRANTED" })
        end
      end
    end
  end
end
