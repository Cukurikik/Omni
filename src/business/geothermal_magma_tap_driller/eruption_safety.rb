module Omni
  module Business
    module GeothermalMagmaTapDriller
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

      class EruptionSafety
        def is_blowout_preventer_required(borehole_pressure_mpa, lithostatic_pressure_mpa)
          if borehole_pressure_mpa < 0 || lithostatic_pressure_mpa < 0
            return OmniResult.new(error: StandardError.new("Pressures must be positive"))
          end

          # Geological Engineering Business Logic: Volcanic Eruption Prevention
          # If we drill directly into a magma chamber to tap unlimited geothermal energy,
          # the pressurized magma might rush up the borehole and trigger an artificial volcanic eruption.
          # We must maintain drilling mud pressure equal to or slightly above the lithostatic pressure.
          
          if borehole_pressure_mpa < lithostatic_pressure_mpa
             return OmniResult.new(value: { 
               safe: false, 
               action: "CRITICAL KICK DETECTED: Borehole pressure underbalanced. Triggering sub-surface Blowout Preventer (BOP) to seal well." 
             })
          end
          
          OmniResult.new(value: { safe: true, action: "Overbalanced drilling maintained. Eruption risk mitigated." })
        end
      end
    end
  end
end
