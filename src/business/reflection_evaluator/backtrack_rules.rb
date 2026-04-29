module Omni
  module Business
    module ReflectionEvaluator
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

      class BacktrackRules
        def determine_next_action(reflection_attempts, confidence_gradient)
          if reflection_attempts < 0
            return OmniResult.new(error: StandardError.new("Attempts cannot be negative"))
          end

          # Reflection Business Logic: Backtracking Rules
          # If the LLM keeps self-critiquing but the answer gets worse or stagnates, force a backtrack
          
          if reflection_attempts >= 3
             return OmniResult.new(value: { action: "FORCE_OUTPUT", reason: "Max reflections reached" })
          end
          
          if confidence_gradient < -0.1
             # Answer got significantly worse after reflection
             return OmniResult.new(value: { action: "BACKTRACK", reason: "Semantic degradation detected" })
          end
          
          if confidence_gradient < 0.01
             return OmniResult.new(value: { action: "RE_SAMPLE", reason: "Stagnant thought process" })
          end
          
          OmniResult.new(value: { action: "ACCEPT_REFINEMENT", reason: "Improvement confirmed" })
        end
      end
    end
  end
end
