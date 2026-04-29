module Omni
  module Business
    module MultiRegionFailover
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

      class RpoRtoRules
        def can_failover(data_lag_seconds, max_rpo_seconds)
          if data_lag_seconds < 0.0 || max_rpo_seconds <= 0.0
            return OmniResult.new(error: StandardError.new("Time constraints must be positive"))
          end

          # Multi-Region Failover Business Logic: Recovery Point Objective (RPO)
          # If a datacenter burns down, we must failover to a backup region.
          # BUT, if the backup region's data is too stale (Data Lag > RPO), failing over
          # could result in unacceptable data loss (e.g., losing millions in financial transactions).
          
          if data_lag_seconds > max_rpo_seconds
             return OmniResult.new(value: { 
               failover_approved: false, 
               reason: "Failover rejected: Data loss would exceed Enterprise RPO SLA limits." 
             })
          end
          
          OmniResult.new(value: { failover_approved: true, reason: "Data synchronization within acceptable RPO limits." })
        end
      end
    end
  end
end
