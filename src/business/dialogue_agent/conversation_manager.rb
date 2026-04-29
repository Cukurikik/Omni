module Omni
  module Business
    module DialogueAgent
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

      class ConversationManager
        def initialize(max_turns: 10)
          @max_turns = max_turns
          @history = []
        end

        def add_turn(user_input: String)
          if user_input.nil? || user_input.empty?
            return OmniResult.new(error: StandardError.new("Input cannot be empty"))
          end

          @history << user_input
          
          if @history.length > @max_turns
            @history.shift # Maintain sliding window
          end

          # Deterministic state hash for memory tracking
          state_hash = @history.join("|").hash

          OmniResult.new(value: {
            turns: @history.length,
            state_hash: state_hash
          })
        end
      end
    end
  end
end
