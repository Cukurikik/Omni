module Omni
  module Business
    module HbmCacheController
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

      class EvictionPriority
        def prioritize_eviction(tensor_type)
          if tensor_type.nil? || tensor_type.empty?
            return OmniResult.new(error: StandardError.new("Tensor type must be specified"))
          end

          # HBM Business Logic: L2 Cache Eviction Rules
          # HBM is incredibly fast but very small. We must aggressively evict the right data.
          
          priority = case tensor_type
          when "ACTIVATION"
             # Activations are temporary during forward pass. Evict immediately after use.
             1
          when "GRADIENT"
             # Gradients needed for backprop, keep longer but evict before weights.
             2
          when "WEIGHT"
             # Model weights are reused constantly. Evict LAST.
             3
          when "KV_CACHE"
             # KV Cache needed for attention generation. Keep as long as context window allows.
             4
          else
             0 # Unknown, evict immediately
          end
          
          OmniResult.new(value: { priority: priority })
        end
      end
    end
  end
end
