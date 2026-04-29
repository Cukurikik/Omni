module Omni
  module Business
    module FlashLoanArbitrage
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

      class GasFeeThresholds
        def is_arbitrage_profitable(gross_profit_usd, estimated_gas_cost_usd)
          if gross_profit_usd < 0 || estimated_gas_cost_usd < 0
            return OmniResult.new(error: StandardError.new("Values must be positive"))
          end

          # Flash Loan Business Logic: Gas Optimization
          # An arbitrage opportunity might yield $500, but if the Ethereum network is congested
          # and the gas fee to execute the complex 4-hop smart contract is $600, you lose money.
          
          net_profit = gross_profit_usd - estimated_gas_cost_usd
          
          if net_profit <= 0
             return OmniResult.new(value: { 
               execute: false, 
               reason: "ABORT: Gas fees exceed gross profit. Net negative EV." 
             })
          end
          
          OmniResult.new(value: { execute: true, net_profit_usd: net_profit })
        end
      end
    end
  end
end
