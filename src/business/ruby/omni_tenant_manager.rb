# OMNI Framework - Tenant Manager (Ruby)
# Core business logic for managing Enterprise tenants and their API keys

require 'securerandom'
require 'json'

module Omni
  class TenantManager
    attr_reader :tenants

    def initialize
      @tenants = {}
      puts "OMNI Ruby: Tenant Manager Initialized."
    end

    def create_tenant(name, tier = 'standard')
      tenant_id = "tnt_#{SecureRandom.hex(8)}"
      api_key = "omni_#{SecureRandom.hex(16)}"
      
      @tenants[tenant_id] = {
        name: name,
        tier: tier,
        api_key: api_key,
        created_at: Time.now.utc,
        active: true
      }
      
      puts "OMNI Ruby: Created Tenant #{name} [#{tenant_id}]"
      
      { tenant_id: tenant_id, api_key: api_key }
    end

    def suspend_tenant(tenant_id)
      if @tenants[tenant_id]
        @tenants[tenant_id][:active] = false
        puts "OMNI Ruby: Suspended Tenant [#{tenant_id}]"
        true
      else
        false
      end
    end

    def export_json
      JSON.pretty_generate(@tenants)
    end
  end
end

# Example usage
# mgr = Omni::TenantManager.new
# mgr.create_tenant("Acme Corp", "enterprise")
