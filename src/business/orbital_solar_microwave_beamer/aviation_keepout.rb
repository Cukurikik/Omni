module Omni
  module Business
    module OrbitalSolarMicrowaveBeamer
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

      class AviationKeepout
        def is_beam_path_clear(commercial_aircraft_proximity_km, minimum_safe_distance_km)
          if commercial_aircraft_proximity_km < 0 || minimum_safe_distance_km <= 0
            return OmniResult.new(error: StandardError.new("Distances must be positive"))
          end

          # Megastructure Business Logic: Aviation Safety
          # A 1 Gigawatt microwave beam from space is basically a giant invisible death ray.
          # If a Boeing 777 flies through the beam path, its electronics will fry and it will heat up.
          # The system must instantly defocus or shut off the beam if an aircraft breaches the keep-out zone.
          
          if commercial_aircraft_proximity_km < minimum_safe_distance_km
             return OmniResult.new(value: { 
               safe: false, 
               action: "EMERGENCY DEFOCUS: Commercial aircraft breached airspace. Scattering microwave array immediately." 
             })
          end
          
          OmniResult.new(value: { safe: true, action: "Airspace clear. Maintained focused Gigawatt power transmission to ground rectenna." })
        end
      end
    end
  end
end
