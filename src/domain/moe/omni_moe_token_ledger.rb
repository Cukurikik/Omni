module Omni
  module Domain
    module MoE
      # OMNI MOTHER Production Zero-Mock Billing Ledger
      # Records exact token consumption per tenant across all MoE active experts

      class InsufficientFundsError < StandardError; end

      class TokenLedger
        attr_reader :tenant_id, :balance_usd, :total_tokens_consumed

        PRICE_PER_1K_TOKENS = {
          "vantage-t5-small" => 0.0001,
          "vibeblade-omni"   => 0.002,
          "expert-math-7b"   => 0.005
        }.freeze

        def initialize(tenant_id, initial_balance_usd = 0.0)
          @tenant_id = tenant_id
          @balance_usd = initial_balance_usd
          @total_tokens_consumed = 0
          @mutex = Mutex.new
          @transactions = []
        end

        def credit(amount_usd)
          @mutex.synchronize do
            raise ArgumentError, "Amount must be positive" if amount_usd <= 0
            @balance_usd += amount_usd
            @transactions << { type: 'CREDIT', amount: amount_usd, timestamp: Time.now.utc }
          end
        end

        def charge_inference(model_id, input_tokens, output_tokens)
          @mutex.synchronize do
            rate = PRICE_PER_1K_TOKENS[model_id]
            raise ArgumentError, "OMNI CRITICAL: Unknown model ID #{model_id}" unless rate

            total_tokens = input_tokens + output_tokens
            cost = (total_tokens.to_f / 1000.0) * rate

            if @balance_usd < cost
              raise InsufficientFundsError, "OMNI CRITICAL: Tenant #{@tenant_id} has insufficient funds (Req: #{cost}, Bal: #{@balance_usd})"
            end

            @balance_usd -= cost
            @total_tokens_consumed += total_tokens
            
            @transactions << { 
              type: 'DEBIT', 
              model: model_id, 
              tokens: total_tokens, 
              cost: cost, 
              timestamp: Time.now.utc 
            }
            
            # Monadic success return
            { success: true, remaining_balance: @balance_usd, cost: cost }
          end
        end

        def generate_report
          @mutex.synchronize do
            {
              tenant_id: @tenant_id,
              balance_usd: @balance_usd.round(4),
              total_tokens: @total_tokens_consumed,
              transaction_count: @transactions.size,
              last_transaction: @transactions.last
            }
          end
        end
      end
    end
  end
end
