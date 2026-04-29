module Omni
  module Business
    module DysonSphereMegastructureArchitect
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

      class IrradianceCapture
        def evaluate_stellar_dimming(capture_percentage, planetary_habitability_required)
          if capture_percentage < 0.0 || capture_percentage > 100.0
            return OmniResult.new(error: StandardError.new("Invalid capture percentage"))
          end

          # Megastructure Business Logic: Stellar Dimming
          # As we build the Dyson Swarm, we block the star's light.
          # If we block too much, any inhabited planets in the system will freeze.
          
          if planetary_habitability_required && capture_percentage > 25.0
             return OmniResult.new(value: { 
               safe: false, 
               action: "ECOLOGICAL_THREAT_WARNING: Irradiance capture exceeding 25%. Solar flux on homeworld dropping below critical thresholds. Global ice age imminent. Halt construction." 
             })
          end
          
          if capture_percentage > 99.0
             return OmniResult.new(value: { 
               safe: true, 
               action: "KARDASHEV_TYPE_II_ACHIEVED: Full Dyson Sphere encapsulation complete. Star visually extinguished from external universe." 
             })
          end
          
          OmniResult.new(value: { safe: true, action: "Swarm construction nominal. Irradiance levels acceptable." })
        end
      end
    end
  end
end
