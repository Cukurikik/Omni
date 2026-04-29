module Omni
  module Business
    module RaftConsensus
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

      class TermProgression
        def evaluate_vote_request(candidate_term, current_term, candidate_last_log_idx, current_last_log_idx)
          # Strict Raft Business Rules for Leader Election safety

          # 1. Reject if candidate's term is older
          if candidate_term < current_term
            return OmniResult.new(value: { grant_vote: false, reason: "TERM_TOO_OLD" })
          end

          # 2. Reject if candidate's log is less up-to-date than ours
          if candidate_last_log_idx < current_last_log_idx
            return OmniResult.new(value: { grant_vote: false, reason: "LOG_NOT_UP_TO_DATE" })
          end

          OmniResult.new(value: { grant_vote: true, reason: "VOTE_GRANTED" })
        end
      end
    end
  end
end
