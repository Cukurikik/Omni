# omni_billing_ledger.rb — AI Inference Billing Ledger
# Layer: Domain / Ruby
#
# Processes inference usage events and calculates token-based billing costs
# for tenant organizations, ensuring real-time quota enforcement.

require 'json'
require 'securerandom'

module Omni
  module Billing
    class Ledger
      PricingTiers = {
        'omni-coco-lm-large' => { prompt: 0.0001, completion: 0.0003 },
        'omni-transquest'    => { prompt: 0.00005, completion: 0.00005 },
        'omni-infini-100k'   => { prompt: 0.0005, completion: 0.001 }
      }.freeze

      def initialize(db_adapter)
        @db = db_adapter
      end

      # Records an inference event and deducts from quota
      def record_inference!(tenant_id, model_name, prompt_tokens, completion_tokens)
        rates = PricingTiers[model_name]
        raise "Model #{model_name} not found in pricing tier" unless rates

        cost = (prompt_tokens * rates[:prompt]) + (completion_tokens * rates[:completion])
        transaction_id = SecureRandom.uuid

        @db.transaction do
          tenant = @db.find_tenant(tenant_id)
          raise "Insufficient quota" if tenant[:balance] < cost

          # Deduct balance
          tenant[:balance] -= cost
          @db.update_tenant(tenant)

          # Record ledger entry
          @db.insert_ledger_entry(
            id: transaction_id,
            tenant_id: tenant_id,
            model: model_name,
            prompt_tokens: prompt_tokens,
            completion_tokens: completion_tokens,
            cost: cost,
            timestamp: Time.now.utc
          )
        end

        { transaction_id: transaction_id, cost: cost, balance: tenant[:balance] }
      end

      def get_usage_report(tenant_id, start_date, end_date)
        entries = @db.query_ledger(tenant_id, start_date, end_date)
        
        total_cost = entries.sum { |e| e[:cost] }
        total_tokens = entries.sum { |e| e[:prompt_tokens] + e[:completion_tokens] }

        {
          tenant_id: tenant_id,
          total_cost: total_cost,
          total_tokens: total_tokens,
          period: "#{start_date} to #{end_date}"
        }
      end
    end
  end
end
