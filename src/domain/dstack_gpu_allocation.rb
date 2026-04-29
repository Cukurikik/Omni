# OMNI Domain Layer - dstack GPU Allocation
module Omni
  module Domain
    module DStack
      class GPUAllocError < StandardError; end

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

      class QuotaValidator
        def validate_gpu_quota(requested, max_quota)
          if requested > max_quota
            Result.new(error: GPUAllocError.new("Requested GPUs exceed tenant quota"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
