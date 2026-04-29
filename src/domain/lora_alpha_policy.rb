# OMNI Domain Layer - LoRA Alpha Policy
module Omni
  module Domain
    module LoRA
      class AlphaError < StandardError; end

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

      class ScalingValidator
        def validate_alpha_ratio(alpha, rank)
          if alpha > rank * 4
            Result.new(error: AlphaError.new("Alpha is too high compared to rank, risks gradient explosion"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
