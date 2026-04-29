module Omni
  module Business
    module SpatialReasoningEngine
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

      class ProximityRules
        def determine_spatial_relationship(distance, bounding_radius_1, bounding_radius_2)
          if distance < 0.0 || bounding_radius_1 <= 0.0 || bounding_radius_2 <= 0.0
            return OmniResult.new(error: StandardError.new("Invalid geometric dimensions"))
          end

          # Spatial Business Logic: Qualitative Physics
          # Translates raw 3D float coordinates into semantic tokens for the LLM
          # E.g., converting distance=0.1 to token="TOUCHING"
          
          collision_dist = bounding_radius_1 + bounding_radius_2
          
          if distance <= collision_dist
             return OmniResult.new(value: "TOUCHING_OR_INTERSECTING")
          elsif distance <= collision_dist * 2.0
             return OmniResult.new(value: "NEARBY")
          else
             return OmniResult.new(value: "FAR_AWAY")
          end
        end
      end
    end
  end
end
