module Omni
  module Business
    module DistributedML
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

      class ClusterManager
        def initialize(max_nodes: 100)
          @max_nodes = max_nodes
        end

        def evaluate_scaling(current_load: Float, current_nodes: Integer)
          return OmniResult.new(error: StandardError.new("Invalid state")) if current_load < 0.0 || current_nodes < 0

          # Deterministic math calculation for scaling
          required_capacity = (current_load * 1.5).ceil
          target_nodes = [required_capacity, @max_nodes].min

          if target_nodes > current_nodes
            OmniResult.new(value: { action: "SCALE_UP", delta: target_nodes - current_nodes })
          elsif target_nodes < current_nodes && current_load < 0.3
            OmniResult.new(value: { action: "SCALE_DOWN", delta: current_nodes - target_nodes })
          else
            OmniResult.new(value: { action: "MAINTAIN", delta: 0 })
          end
        end
      end
    end
  end
end
