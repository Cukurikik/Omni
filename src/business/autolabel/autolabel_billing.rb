# OMNI Business Layer: autolabel_billing.rb
# Ruby domain logic for calculating AutoLabel API usage billing.
# Bound: Max 1,000,000 tokens billed per transaction.

module Omni
  module AutoLabel
    MAX_TOKENS_PER_TX = 1_000_000
    RATE_PER_1K_TOKENS = 0.02 # USD

    class OmniError < StandardError
      attr_reader :code
      def initialize(code, msg)
        @code = code
        super(msg)
      end
    end

    class OmniResult
      attr_reader :data, :error
      def initialize(data, error = nil)
        @data = data
        @error = error
      end
    end

    class BillingEngine
      def calculate_cost(tokens_used)
        if tokens_used > MAX_TOKENS_PER_TX
          return OmniResult.new(nil, OmniError.new(1, "Transaction exceeds 1M token billing limit."))
        end
        
        cost = (tokens_used.to_f / 1000.0) * RATE_PER_1K_TOKENS
        OmniResult.new(cost.round(4))
      end
    end
  end
end
