module Omni
  module Business
    module xLSTMModel
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

      class SequenceLimits
        def initialize(max_seq_length: 4096)
          @max_length = max_seq_length
        end

        def validate_and_truncate(sequence: Array)
          if sequence.nil? || sequence.empty?
            return OmniResult.new(error: StandardError.new("Sequence cannot be empty"))
          end

          # Business Logic: Enforce strict memory bounds for xLSTM context
          if sequence.size > @max_length
            # Truncate keeping the most recent tokens (right-side alignment)
            truncated = sequence.last(@max_length)
            return OmniResult.new(value: { sequence: truncated, truncated: true })
          end

          OmniResult.new(value: { sequence: sequence, truncated: false })
        end
      end
    end
  end
end
