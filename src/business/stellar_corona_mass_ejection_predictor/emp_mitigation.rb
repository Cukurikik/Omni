module Omni
  module Business
    module StellarCoronaMassEjectionPredictor
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

      class EmpMitigation
        def evaluate_carrington_event_threat(cme_velocity_km_s, earth_directed)
          if cme_velocity_km_s < 0.0
            return OmniResult.new(error: StandardError.new("Velocity cannot be negative"))
          end

          # Planetary Defense Business Logic: EMP Mitigation
          # A Carrington-class event (massive CME hitting Earth) will induce massive
          # geomagnetically induced currents (GICs), destroying the global power grid
          # and returning civilization to the 18th century. We must provide advance warning.
          
          if earth_directed && cme_velocity_km_s > 2000.0
             # At 2000 km/s, the CME will reach Earth in ~20 hours.
             return OmniResult.new(value: { 
               threat_level: "EXTREME", 
               action: "CARRINGTON_EVENT_DETECTED: Initiate global power grid shutdown immediately. Disconnect all large-scale transformers from the network." 
             })
          elsif earth_directed && cme_velocity_km_s > 800.0
             return OmniResult.new(value: { 
               threat_level: "HIGH", 
               action: "G2_GEOMAGNETIC_STORM: Expect satellite drag anomalies and high-latitude radio blackouts. Aurora visible at lower latitudes." 
             })
          end
          
          OmniResult.new(value: { threat_level: "NORMAL", action: "Solar weather nominal. No planetary threat." })
        end
      end
    end
  end
end
