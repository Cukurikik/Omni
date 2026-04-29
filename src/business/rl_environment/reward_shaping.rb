module Omni
  module Business
    module RLEnvironment
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

      class RewardShaping
        def initialize(goal_pos_x: 10.0)
          @goal_pos_x = goal_pos_x
        end

        def calculate_shaped_reward(current_x: Float, prev_x: Float, base_reward: Float)
          if current_x.nil? || prev_x.nil?
            return OmniResult.new(error: StandardError.new("Positions cannot be nil"))
          end

          # Business logic: Potential-based reward shaping
          # F(s, s') = gamma * Phi(s') - Phi(s)
          # Here, Phi is the negative distance to the goal
          
          prev_distance = (@goal_pos_x - prev_x).abs
          current_distance = (@goal_pos_x - current_x).abs
          
          # Reward moving closer to the goal
          shaping_term = prev_distance - current_distance
          
          final_reward = base_reward + shaping_term

          OmniResult.new(value: final_reward)
        end
      end
    end
  end
end
