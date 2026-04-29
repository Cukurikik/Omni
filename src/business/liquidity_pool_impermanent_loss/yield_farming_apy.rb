module Omni
  module Business
    module LiquidityPoolImpermanentLoss
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

      class YieldFarmingApy
        def is_liquidity_profitable(yield_farm_apy_percent, impermanent_loss_percent)
          if yield_farm_apy_percent < 0 || impermanent_loss_percent < 0
            return OmniResult.new(error: StandardError.new("Percentages must be positive"))
          end

          # DeFi Business Logic: APY vs Impermanent Loss
          # Yield farming provides high APY rewards. However, if the tokens are highly volatile,
          # the Impermanent Loss will eat all the yield and the user will lose money overall.
          
          net_yield = yield_farm_apy_percent - impermanent_loss_percent
          
          if net_yield < 0.0
             return OmniResult.new(value: { 
               profitable: false, 
               reason: "WARNING: Impermanent Loss (-#{impermanent_loss_percent}%) exceeds Farming Yield (+#{yield_farm_apy_percent}%). Net negative return." 
             })
          end
          
          OmniResult.new(value: { profitable: true, net_yield_percent: net_yield })
        end
      end
    end
  end
end
