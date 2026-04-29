module Omni
  module Business
    module DiamondRL
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

      class RewardPolicy
        def initialize(max_reward: 100.0, penalty: -10.0)
          @max_reward = max_reward
          @penalty = penalty
        end

        def evaluate_action(state_diff, goal_distance)
          if state_diff.nil? || goal_distance.nil? || goal_distance < 0
            return OmniResult.new(error: StandardError.new("Invalid state or distance variables"))
          end

          # Business Rules: Compute RL reward based on deterministic state differences
          # If distance is decreasing, positive reward. If increasing, penalty.
          
          if state_diff > 0
            # Moving towards goal
            reward = [state_diff * 10.0, @max_reward].min
          else
            # Moving away or stationary
            reward = @penalty
          end

          # Add proximity bonus
          if goal_distance < 1.0
            reward += 50.0 # Terminal success state bonus
          end

          OmniResult.new(value: { reward: reward, is_terminal: goal_distance < 1.0 })
        end
      end
    end
  end
end
