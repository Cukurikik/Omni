module Omni
  module Business
    module FastquantBacktester
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

      class DrawdownRules
        def evaluate_strategy_risk(max_drawdown_pct, sharpe_ratio)
          if max_drawdown_pct < 0.0 || max_drawdown_pct > 1.0
            return OmniResult.new(error: StandardError.new("Drawdown percentage must be between 0.0 and 1.0"))
          end

          # FastQuant Business Logic: Institutional Risk Management
          if max_drawdown_pct >= 0.25
            return OmniResult.new(value: { 
              status: "REJECTED", 
              reason: "Max drawdown exceeds 25% institutional limit",
              action: "RE_TUNE_HYPERPARAMETERS"
            })
          end

          if sharpe_ratio < 1.0
            return OmniResult.new(value: {
              status: "REJECTED",
              reason: "Sharpe ratio < 1.0 indicates poor risk-adjusted returns",
              action: "DISCARD_STRATEGY"
            })
          end

          OmniResult.new(value: { status: "APPROVED", action: "DEPLOY_TO_PAPER_TRADING" })
        end
      end
    end
  end
end
