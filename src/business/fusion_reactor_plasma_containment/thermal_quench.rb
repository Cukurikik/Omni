module Omni
  module Business
    module FusionReactorPlasmaContainment
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

      class ThermalQuench
        def evaluate_disruption_risk(plasma_beta, troyon_limit, temperature_kelvin)
          if troyon_limit <= 0 || temperature_kelvin < 0
            return OmniResult.new(error: StandardError.new("Limits and temp must be positive"))
          end

          # Plasma Physics Business Logic: Thermal Quench Safety
          # If the plasma beta exceeds the Troyon stability limit, the plasma will touch the tokamak walls.
          # At 150 million degrees, this will melt the beryllium tiles instantly. We must inject argon gas to quench it.
          
          if plasma_beta > troyon_limit
             return OmniResult.new(value: { 
               safe: false, 
               reason: "CRITICAL: Troyon limit exceeded (Beta: #{plasma_beta.round(3)}). Initiating Massive Gas Injection (MGI) for thermal quench." 
             })
          end
          
          OmniResult.new(value: { safe: true, reason: "Plasma stable. Containment maintained." })
        end
      end
    end
  end
end
