module Omni
  module Business
    module CloudCostOptimizer
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

      class FinopsAlerting
        def should_trigger_burn_alert(current_monthly_spend, monthly_budget, days_into_month)
          if current_monthly_spend < 0.0 || monthly_budget <= 0.0 || days_into_month <= 0
            return OmniResult.new(error: StandardError.new("FinOps metrics must be positive"))
          end

          # Cloud Cost Business Logic: FinOps Budget Forecasting
          # If the current run-rate suggests we will blow past the budget, trigger a P1 alert to engineering.
          
          # Linear projection of end-of-month spend
          projected_total = (current_monthly_spend / days_into_month) * 30.0
          
          if projected_total > (monthly_budget * 1.10) # Allow 10% variance
             return OmniResult.new(value: { 
               alert: true, 
               reason: "Projected spend exceeds budget by >10%. Immediate FinOps intervention required." 
             })
          end
          
          OmniResult.new(value: { alert: false, reason: "Burn rate nominal." })
        end
      end
    end
  end
end
