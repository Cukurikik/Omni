# OMNI Domain Layer - xLSTM Architecture
module Omni
  module Domain
    module xLSTM
      class ArchError < StandardError; end

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

      class NetworkValidator
        def validate_block_ratio(slstm_blocks, mlstm_blocks)
          if mlstm_blocks == 0 && slstm_blocks > 0
            Result.new(error: ArchError.new("xLSTM requires at least one mLSTM block for memory parallelization"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
