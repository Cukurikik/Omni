module Omni
  module Business
    module OfflineSyncManager
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

      class StalenessPolicies
        def can_use_local_cache(hours_offline, is_critical_financial_data)
          if hours_offline < 0.0
            return OmniResult.new(error: StandardError.new("Offline duration cannot be negative"))
          end

          # Offline Sync Business Logic: Data Staleness
          # Determines if an offline Edge device is allowed to proceed using its cached data,
          # or if the operation must be blocked until a network connection is re-established
          
          if is_critical_financial_data
             if hours_offline > 1.0
                 return OmniResult.new(value: { 
                   allowed: false, 
                   reason: "Financial data cache expired. Network connection required." 
                 })
             end
          else
             # Non-critical data (e.g. LLM context) can stay stale for up to 72 hours
             if hours_offline > 72.0
                 return OmniResult.new(value: { 
                   allowed: false, 
                   reason: "General data cache expired after 72 hours offline." 
                 })
             end
          end
          
          OmniResult.new(value: { allowed: true, reason: "Local cache is within acceptable staleness limits." })
        end
      end
    end
  end
end
