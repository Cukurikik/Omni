module Omni
  module Business
    module StellarEngineShkadovThruster
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

      class GalacticAstrogation
        def evaluate_stellar_trajectory(thrust_newtons, system_mass_kg, travel_time_years)
          if thrust_newtons < 0.0 || system_mass_kg <= 0.0 || travel_time_years < 0.0
            return OmniResult.new(error: StandardError.new("Invalid orbital parameters"))
          end

          # Astrogation Business Logic: Moving a Solar System
          # A Shkadov thruster moves the entire solar system to avoid galactic hazards
          # (like supernovas or black holes) or to rendezvous with other systems.
          # The acceleration is incredibly small, but acts over millions of years.
          
          # F = ma -> a = F/m
          acceleration_m_s2 = thrust_newtons / system_mass_kg
          
          travel_time_seconds = travel_time_years * 31536000.0
          
          # d = 1/2 a t^2
          distance_moved_meters = 0.5 * acceleration_m_s2 * (travel_time_seconds ** 2)
          distance_lightyears = distance_moved_meters / 9.461e15
          
          if distance_lightyears < 10.0 && travel_time_years > 1_000_000.0
             return OmniResult.new(value: { 
               safe: false, 
               action: "HAZARD_AVOIDANCE_FAILED: Thrust insufficient. System will not clear the blast radius of the pending Betelgeuse supernova in time. Increase mirror coverage." 
             })
          end
          
          OmniResult.new(value: { safe: true, action: "Trajectory optimal. Solar system successfully deviating from natural galactic orbit." })
        end
      end
    end
  end
end
