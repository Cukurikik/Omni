module Omni
  module Business
    module DeepSpaceNetworkRelay
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

      class AntennaPriority
        def check_dsn_allocation(mission_criticality, requested_duration_hrs)
          if requested_duration_hrs <= 0
            return OmniResult.new(error: StandardError.new("Duration must be positive"))
          end

          # Space Communications Business Logic: DSN Antenna Contention
          # The Deep Space Network (Madrid, Goldstone, Canberra) has limited 70-meter dishes.
          # We must ruthlessly prioritize which spacecraft get to phone home.
          
          if mission_criticality == "CRITICAL_ENTRY_DESCENT_LANDING"
             return OmniResult.new(value: { 
               approved: true, 
               reason: "EDL Override: Granted immediate preemptive access to 70m Goldstone Array." 
             })
          end
          
          if requested_duration_hrs > 4.0
             return OmniResult.new(value: { 
               approved: false, 
               reason: "DENIED: Routine telemetry dumps cannot exceed 4 hours per pass due to Voyager 1 contention." 
             })
          end
          
          OmniResult.new(value: { approved: true, reason: "Routine pass scheduled." })
        end
      end
    end
  end
end
