module Omni
  module Business
    module ReactReasoningLoop
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

      class TokenLimits
        def evaluate_loop_continuation(current_tokens_spent, max_budget, loop_count)
          if current_tokens_spent < 0 || max_budget <= 0
            return OmniResult.new(error: StandardError.new("Token metrics must be positive"))
          end

          # ReAct Business Logic: Infinite Loop Prevention
          # LLM Agents can get stuck in loops (Thought -> Action -> Obs -> Thought...)
          # This enforces strict token limits and loop bounds
          
          if current_tokens_spent > max_budget
             return OmniResult.new(value: { continue: false, reason: "BUDGET_EXCEEDED" })
          end
          
          if loop_count > 15
             # Hard cutoff to prevent runaway inference costs
             return OmniResult.new(value: { continue: false, reason: "MAX_ITERATIONS_REACHED" })
          end
          
          OmniResult.new(value: { continue: true, reason: "WITHIN_LIMITS" })
        end
      end
    end
  end
end
