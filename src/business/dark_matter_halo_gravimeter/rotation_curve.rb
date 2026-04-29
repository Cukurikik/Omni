module Omni
  module Business
    module DarkMatterHaloGravimeter
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

      class RotationCurve
        def evaluate_galactic_stability(visible_mass_solar_masses, dark_matter_density_gev_cm3)
          if visible_mass_solar_masses <= 0.0 || dark_matter_density_gev_cm3 < 0.0
            return OmniResult.new(error: StandardError.new("Invalid galactic mass parameters"))
          end

          # Astrophysics Business Logic: Galactic Rotation Curve
          # Galaxies spin so fast that the visible matter (stars/gas) doesn't have enough
          # gravity to hold them together; they should fly apart.
          # The Dark Matter Halo provides the invisible gravitational glue.
          
          # If the ratio of Dark Matter to Visible Matter is too low, the galaxy will disintegrate.
          critical_dm_density = 0.1 # GeV/cm^3
          
          if dark_matter_density_gev_cm3 < critical_dm_density
             return OmniResult.new(value: { 
               stable: false, 
               action: "GALACTIC_DISINTEGRATION_WARNING: Dark matter halo depleted. Centrifugal forces exceeding gravitational binding energy. Star systems will be ejected into intergalactic space." 
             })
          end
          
          OmniResult.new(value: { stable: true, action: "Rotation curve flat. Galactic structural integrity nominal." })
        end
      end
    end
  end
end
