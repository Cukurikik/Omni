module Omni
  module Business
    module EdgeDeviceRouter
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

      class GeofencingRules
        def allowed_to_route(device_region, edge_node_region, data_sensitivity)
          if device_region.nil? || edge_node_region.nil?
            return OmniResult.new(error: StandardError.new("Regions must be specified"))
          end

          # Edge Router Business Logic: Geofencing & Data Sovereignty
          # Strict enforcement of data privacy laws (e.g., GDPR)
          # Highly sensitive data must not cross continental/legal boundaries
          
          if data_sensitivity == "HIGH" || data_sensitivity == "TOP_SECRET"
             if device_region != edge_node_region
                 return OmniResult.new(value: { 
                   allowed: false, 
                   reason: "Data sovereignty violation: Sensitive data cannot cross regions." 
                 })
             end
          end
          
          OmniResult.new(value: { allowed: true, reason: "Routing permitted by policy." })
        end
      end
    end
  end
end
