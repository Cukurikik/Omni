module Omni
  module Business
    module VonNeumannProbeReplicator
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

      class GreyGooContainment
        def evaluate_replication_limits(current_swarm_mass_kg, planetary_mass_kg)
          if current_swarm_mass_kg < 0.0 || planetary_mass_kg <= 0.0
            return OmniResult.new(error: StandardError.new("Invalid swarm mass parameters"))
          end

          # Cybernetics Business Logic: Grey Goo Prevention
          # If self-replicating machines are not given a hard limit, they will
          # consume all matter in the solar system to make more copies of themselves.
          # We must enforce a strict mass-ratio limit (e.g., 0.0001% of an asteroid's mass).
          
          mass_ratio = current_swarm_mass_kg / planetary_mass_kg
          critical_limit = 1.0e-6 # 0.0001%
          
          if mass_ratio > critical_limit
             return OmniResult.new(value: { 
               safe: false, 
               action: "GREY_GOO_SCENARIO_DETECTED: Swarm mass exceeding ecological limits. Initiating remote self-destruct protocol to prevent total planetary disassembly." 
             })
          end
          
          OmniResult.new(value: { safe: true, action: "Replication within bounds. Continue asteroid mining operations." })
        end
      end
    end
  end
end
