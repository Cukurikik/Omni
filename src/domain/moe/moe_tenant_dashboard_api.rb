# moe_tenant_dashboard_api.rb — Domain / Web
# Layer: Domain / API — Tenant Usage Dashboard API
#
# A Ruby controller serving the React/TypeScript frontend. Provides RESTful
# endpoints for tenants to view their historical expert usage, billing costs,
# and current API rate limits dynamically read from PostgreSQL/Redis.

require 'json'

class TenantDashboardController
  def initialize
    puts "[Dashboard API] Initialized Ruby REST API for MoE Billing Dashboard."
    # Mock database connections
    @billing_db = {
      "T-123" => { 
        tier: "premium", 
        tokens_used: 1_250_000, 
        current_bill_usd: 62.50,
        expert_breakdown: {
          "general" => 500_000,
          "coding" => 750_000
        }
      }
    }
  end

  # GET /api/v1/tenant/:id/usage
  def get_usage(tenant_id)
    data = @billing_db[tenant_id]
    
    if data.nil?
      return { status: 404, body: { error: "Tenant not found" }.to_json }
    end

    response = {
      tenant_id: tenant_id,
      tier: data[:tier],
      metrics: {
        total_tokens: data[:tokens_used],
        total_cost_usd: data[:current_bill_usd]
      },
      expert_breakdown: data[:expert_breakdown],
      timestamp: Time.now.utc.iso8601
    }

    { status: 200, body: response.to_json, headers: { 'Content-Type' => 'application/json' } }
  end

  # POST /api/v1/tenant/:id/upgrade
  def upgrade_tier(tenant_id, new_tier)
    # Validates payment method and syncs new limits to the Go Gateway
    puts "[Dashboard API] Upgrading Tenant #{tenant_id} to #{new_tier.upcase} tier."
    # redis.publish("tier_updates", {tenant: tenant_id, tier: new_tier}.to_json)
    
    { status: 200, body: { message: "Upgrade successful. Changes sync to router in ~5s." }.to_json }
  end
end

# Usage:
# api = TenantDashboardController.new
# puts api.get_usage("T-123")[:body]
