module Omni
  module Business
    module DefiAmmPricingCurve
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

      class SlippageTolerance
        def is_swap_acceptable(expected_output, actual_output, max_slippage_percent)
          if expected_output <= 0 || actual_output <= 0 || max_slippage_percent < 0
            return OmniResult.new(error: StandardError.new("Values must be positive"))
          end

          # DeFi Business Logic: Slippage Protection
          # When swapping tokens on a decentralized exchange, the price might change 
          # before the transaction is mined (due to front-running or high volatility).
          # Users set a maximum slippage tolerance (e.g., 1%). If actual output drops below that, revert.
          
          min_acceptable_output = expected_output * (1.0 - (max_slippage_percent / 100.0))
          
          if actual_output < min_acceptable_output
             return OmniResult.new(value: { 
               acceptable: false, 
               reason: "REVERT: Actual output fell below minimum acceptable amount due to high slippage." 
             })
          end
          
          OmniResult.new(value: { acceptable: true, reason: "Swap execution within slippage tolerance." })
        end
      end
    end
  end
end
