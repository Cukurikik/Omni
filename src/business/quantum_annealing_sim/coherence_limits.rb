module Omni
  module Business
    module QuantumAnnealingSim
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

      class CoherenceLimits
        def is_anneal_schedule_valid(anneal_time_microseconds, hardware_t2_coherence_time)
          if anneal_time_microseconds <= 0.0 || hardware_t2_coherence_time <= 0.0
            return OmniResult.new(error: StandardError.new("Times must be positive"))
          end

          # Quantum Business Logic: Coherence Time Constraints
          # If the annealing schedule takes longer than the quantum state can remain coherent (T2 time),
          # the qubits will decohere (collapse) into classical thermal noise, ruining the calculation.
          
          if anneal_time_microseconds > (hardware_t2_coherence_time * 0.8)
             # Leave a 20% safety margin before decoherence
             return OmniResult.new(value: { 
               valid: false, 
               reason: "Annealing schedule too slow. Exceeds T2 quantum decoherence safety limits." 
             })
          end
          
          OmniResult.new(value: { valid: true, reason: "Schedule within coherence bounds." })
        end
      end
    end
  end
end
