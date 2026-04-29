# OMNI Domain Layer - ReinFlow Action Space
module Omni
  module Domain
    module ReinFlow
      class ActionSpaceError < StandardError; end

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

      class Validator
        def validate_gripper_action(gripper_val)
          if gripper_val < -1.0 || gripper_val > 1.0
            Result.new(error: ActionSpaceError.new("Gripper action must be normalized [-1, 1]"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
