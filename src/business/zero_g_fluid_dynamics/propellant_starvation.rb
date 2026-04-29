module Omni
  module Business
    module ZeroGFluidDynamics
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

      class PropellantStarvation
        def is_thruster_firing_safe(liquid_at_intake_percent)
          if liquid_at_intake_percent < 0.0 || liquid_at_intake_percent > 100.0
            return OmniResult.new(error: StandardError.new("Percentage must be 0-100"))
          end

          # Microgravity Business Logic: Thruster Cavitation Prevention
          # In Zero-G, propellant floats. If an orbital maneuvering thruster fires while 
          # helium gas is at the intake instead of liquid hydrazine, the engine will explode.
          
          if liquid_at_intake_percent < 98.0
             return OmniResult.new(value: { 
               safe_to_fire: false, 
               reason: "DANGER: Gas bubble detected at thruster intake. Perform ullage motor burn first to settle propellant." 
             })
          end
          
          OmniResult.new(value: { safe_to_fire: true, reason: "Propellant settled. Ready for ignition." })
        end
      end
    end
  end
end
