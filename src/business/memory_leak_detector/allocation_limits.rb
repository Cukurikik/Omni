module Omni
  module Business
    module MemoryLeakDetector
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

      class AllocationLimits
        def evaluate_leak_severity(growth_rate_mb, time_elapsed_minutes)
          if growth_rate_mb < 0.0 || time_elapsed_minutes <= 0.0
            return OmniResult.new(error: StandardError.new("Invalid metrics"))
          end

          # Memory Leak Business Logic: Severity Thresholds
          # Defines when a detected memory growth pattern transitions from "normal caching" to a "critical leak"
          
          total_growth_per_hour = growth_rate_mb * (60.0 / time_elapsed_minutes)
          
          if total_growth_per_hour > 500.0
             # Growing by 500MB+ per hour is an immediate OOM risk
             return OmniResult.new(value: { severity: "CRITICAL", action: "RESTART_AND_ROLLBACK" })
          end
          
          if total_growth_per_hour > 50.0
             return OmniResult.new(value: { severity: "WARNING", action: "ALERT_ENGINEERING" })
          end
          
          OmniResult.new(value: { severity: "NORMAL", action: "NONE" })
        end
      end
    end
  end
end
