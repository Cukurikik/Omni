module Omni
  module Business
    module OptionsPricingBlackScholes
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

      class GreeksRiskLimits
        def check_portfolio_gamma(current_gamma, max_gamma_limit)
          if max_gamma_limit <= 0
            return OmniResult.new(error: StandardError.new("Limit must be positive"))
          end

          # Options Trading Business Logic: Gamma Risk Management
          # Gamma measures the rate of change of Delta. High Gamma means extreme sensitivity to underlying price swings.
          # Trading desks enforce strict Gamma limits to prevent catastrophic blowups during market crashes.
          
          if current_gamma.abs > max_gamma_limit
             return OmniResult.new(value: { 
               approved: false, 
               reason: "RISK LIMIT EXCEEDED: Portfolio Gamma exceeds maximum allowed threshold. Mandatory hedging required." 
             })
          end
          
          OmniResult.new(value: { approved: true, reason: "Portfolio Gamma within acceptable risk limits." })
        end
      end
    end
  end
end
