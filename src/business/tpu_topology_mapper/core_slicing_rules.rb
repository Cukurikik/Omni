module Omni
  module Business
    module TpuTopologyMapper
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

      class CoreSlicingRules
        def can_slice_tpu_pod(requested_cores, available_topology)
          if requested_cores <= 0
            return OmniResult.new(error: StandardError.new("Requested cores must be positive"))
          end

          # TPU Business Logic: Core Slicing Constraints
          # Google TPUs can only be sliced in specific powers of two (e.g., v4-8, v4-32, v4-128)
          # You cannot request an arbitrary number of cores like 17 or 50.
          
          is_power_of_two = (requested_cores & (requested_cores - 1)) == 0
          
          if !is_power_of_two
             return OmniResult.new(value: { 
               allowed: false, 
               reason: "TPU Pod slices must be powers of 2 (8, 32, 64, 128, etc.)." 
             })
          end
          
          if requested_cores < 8
             return OmniResult.new(value: { 
               allowed: false, 
               reason: "Minimum slice for standard TPU Pod is 8 cores." 
             })
          end
          
          OmniResult.new(value: { allowed: true, reason: "Valid TPU Pod slice request." })
        end
      end
    end
  end
end
