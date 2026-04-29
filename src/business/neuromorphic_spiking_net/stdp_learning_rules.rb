module Omni
  module Business
    module NeuromorphicSpikingNet
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

      class StdpLearningRules
        def compute_weight_update(time_pre_spike, time_post_spike, current_weight, max_weight)
          if time_pre_spike < 0.0 || time_post_spike < 0.0 || max_weight <= 0.0
            return OmniResult.new(error: StandardError.new("Invalid spike timing parameters"))
          end

          # Neuromorphic Business Logic: Spike-Timing-Dependent Plasticity (STDP)
          # "Neurons that fire together, wire together."
          # If pre fires BEFORE post -> strengthen connection (LTP)
          # If pre fires AFTER post -> weaken connection (LTD)
          
          delta_t = time_post_spike - time_pre_spike
          
          # STDP Constants
          a_plus = 0.01  # Learning rate LTP
          a_minus = 0.012 # Learning rate LTD
          tau = 20.0      # Time constant (ms)
          
          new_weight = current_weight
          
          if delta_t > 0
             # LTP (Long-Term Potentiation)
             dw = a_plus * Math.exp(-delta_t / tau)
             new_weight += dw
          elsif delta_t < 0
             # LTD (Long-Term Depression)
             dw = -a_minus * Math.exp(delta_t / tau)
             new_weight += dw
          end
          
          # Clamp to [0, max_weight]
          new_weight = [0.0, [new_weight, max_weight].min].max
          
          OmniResult.new(value: { new_weight: new_weight, delta_w: new_weight - current_weight })
        end
      end
    end
  end
end
