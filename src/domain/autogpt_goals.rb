# OMNI Domain Layer - AutoGPT Goals
module Omni
  module Domain
    module AutoGPT
      class GoalError < StandardError; end

      class Result
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class GoalValidator
        def validate_goal_depth(sub_goals)
          if sub_goals.length > 50
            Result.new(error: GoalError.new("Too many sub-goals. Maximum is 50."))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
