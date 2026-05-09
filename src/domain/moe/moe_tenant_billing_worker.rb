# moe_tenant_billing_worker.rb — Domain / Billing
# Layer: Domain / Business Logic — MoE Expert Billing
#
# A Ruby background worker that ingests logs/metrics from the Go Gateway
# and calculates tenant billing. Premium experts (e.g. Legal, Medical) 
# cost more tokens than general chat experts.

require 'json'
require 'net/http'

class TenantBillingWorker
  EXPERT_PRICING_TIERS = {
    standard: 0.0001,   # $0.0001 per token
    premium: 0.0005,    # $0.0005 per token (Coding, Analytics)
    enterprise: 0.0020  # $0.0020 per token (Medical, Legal)
  }

  def initialize
    puts "[Billing Worker] Initialized MoE Billing Processor."
    @tenant_ledgers = Hash.new(0.0)
  end

  def process_usage_batch(batch_json)
    usage_data = JSON.parse(batch_json)
    
    usage_data.each do |record|
      tenant_id = record['tenant_id']
      tokens = record['tokens_processed']
      tier = record['expert_tier'].to_sym

      rate = EXPERT_PRICING_TIERS[tier] || EXPERT_PRICING_TIERS[:standard]
      cost = tokens * rate
      
      @tenant_ledgers[tenant_id] += cost
    end
    
    sync_to_database()
  end

  def get_current_bill(tenant_id)
    @tenant_ledgers[tenant_id].round(4)
  end

  private

  def sync_to_database
    # Mocking database sync
    @tenant_ledgers.each do |tenant, cost|
      puts "[Billing Worker] Synced Tenant #{tenant} | Accrued Cost: $#{cost.round(4)}"
    end
  end
end

# Example usage trigger
# worker = TenantBillingWorker.new
# worker.process_usage_batch('[{"tenant_id": "T-123", "tokens_processed": 5000, "expert_tier": "premium"}]')
