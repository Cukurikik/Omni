module Omni
  module Business
    module RdmaMemoryBridge
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

      class NumaPinningRules
        def check_numa_alignment(gpu_numa_node, nic_numa_node)
          if gpu_numa_node < 0 || nic_numa_node < 0
            return OmniResult.new(error: StandardError.new("NUMA nodes must be non-negative integers"))
          end

          # RDMA Business Logic: NUMA Topology Alignment
          # For zero-copy RDMA to work at max speed (e.g. GPU Direct RDMA), 
          # the GPU and the Network Interface Card (NIC) MUST be attached to the same CPU/PCIe Root Complex.
          
          if gpu_numa_node != nic_numa_node
             return OmniResult.new(value: { 
               aligned: false, 
               reason: "NUMA Mismatch. GPU and NIC are on different PCIe root complexes. RDMA will fallback to slow QPI/UPI links." 
             })
          end
          
          OmniResult.new(value: { aligned: true, reason: "Hardware perfectly aligned for GPU-Direct RDMA." })
        end
      end
    end
  end
end
