# OMNI Domain Layer - DeepSpeed Stage Policy
module Omni
  module Domain
    module DeepSpeed
      class StageError < StandardError; end

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

      class PolicyValidator
        def validate_zero_stage(stage, offload)
          if offload && stage < 2
            Result.new(error: StageError.new("CPU Offload requires ZeRO Stage 2 or 3"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
