module Omni
  module Business
    module AlkaliMetalIonThruster
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

      class DeltaVEconomy
        def evaluate_burn_profile(delta_v_required_km_s, propellant_mass_fraction)
          if delta_v_required_km_s < 0.0 || propellant_mass_fraction <= 0.0 || propellant_mass_fraction >= 1.0
            return OmniResult.new(error: StandardError.new("Invalid orbital mechanics parameters"))
          end

          # Astronautics Business Logic: Deep Space Delta-V Economy
          # Chemical rockets use fuel fast. Ion drives thrust very weakly but continuously
          # for years, eventually reaching incredible speeds. We use the Tsiolkovsky rocket equation
          # to ensure we don't run out of Xenon gas before reaching the destination.
          
          # Max theoretical Delta-V based on a specific impulse (Isp) of 3000s
          effective_exhaust_velocity_km_s = 30.0 
          max_delta_v = effective_exhaust_velocity_km_s * Math.log(1.0 / (1.0 - propellant_mass_fraction))
          
          if delta_v_required_km_s > max_delta_v
             return OmniResult.new(value: { 
               viable: false, 
               action: "MISSION_ABORT: Required Delta-V exceeds propellant mass fraction limits. Ship will be stranded in deep space." 
             })
          end
          
          OmniResult.new(value: { viable: true, action: "Trajectory locked. Commencing continuous multi-year ion burn." })
        end
      end
    end
  end
end
