module Omni
  module Business
    module RateLimiter
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

      class SLATiering
        def get_tier_limits(tier_level)
          if tier_level.nil? || tier_level.empty?
            return OmniResult.new(error: StandardError.new("SLA tier level cannot be empty"))
          end

          # Business rules defining request thresholds per SLA tier
          case tier_level.upcase
          when "FREE"
            OmniResult.new(value: { burst_capacity: 10.0, refill_rate_per_sec: 1.0 })
          when "BASIC"
            OmniResult.new(value: { burst_capacity: 100.0, refill_rate_per_sec: 10.0 })
          when "ENTERPRISE"
            OmniResult.new(value: { burst_capacity: 5000.0, refill_rate_per_sec: 1000.0 })
          else
            OmniResult.new(error: StandardError.new("Unknown SLA tier level"))
          end
        end
      end
    end
  end
end
