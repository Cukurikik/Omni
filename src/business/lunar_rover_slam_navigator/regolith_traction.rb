module Omni
  module Business
    module LunarRoverSlamNavigator
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

      class RegolithTraction
        def validate_path_incline(proposed_incline_degrees, max_safe_incline_degrees)
          if max_safe_incline_degrees <= 0
            return OmniResult.new(error: StandardError.new("Incline limits must be positive"))
          end

          # Planetary Exploration Business Logic: Regolith Slippage
          # Lunar soil (regolith) is extremely loose. If SLAM proposes a path up a crater wall 
          # that exceeds the physical friction coefficient of the rover's wheels, it will slide back and flip.
          
          if proposed_incline_degrees > max_safe_incline_degrees
             return OmniResult.new(value: { 
               safe: false, 
               reason: "ABORT: Proposed trajectory exceeds maximum regolith traction incline. Rerouting." 
             })
          end
          
          OmniResult.new(value: { safe: true, reason: "Path incline within nominal traction limits." })
        end
      end
    end
  end
end
