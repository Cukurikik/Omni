# omni_billing_api.rb — Billing API Endpoints
# Layer: Domain / Ruby
#
# Provides a simple REST API to interact with the OmniBillingLedger,
# allowing tenant usage querying and manual transaction additions.

require 'json'
# Mock Rack integration
# require 'rack'

module Omni
  module Finances
    class BillingAPI
      def initialize(ledger)
        @ledger = ledger
      end

      def call(env)
        req = Rack::Request.new(env)
        
        if req.path.match(%r{^/api/billing/usage/(.+)$}) && req.get?
          tenant_id = $1
          handle_get_usage(tenant_id, req.params)
        elsif req.path == '/api/billing/transaction' && req.post?
          handle_post_transaction(req)
        else
          [404, { 'Content-Type' => 'application/json' }, [{ error: 'Not Found' }.to_json]]
        end
      end

      private

      def handle_get_usage(tenant_id, params)
        start_date = params['start'] || (Time.now - 30 * 24 * 60 * 60).to_s
        end_date = params['end'] || Time.now.to_s
        
        begin
          report = @ledger.get_usage_report(tenant_id, start_date, end_date)
          [200, { 'Content-Type' => 'application/json' }, [report.to_json]]
        rescue => e
          [500, { 'Content-Type' => 'application/json' }, [{ error: e.message }.to_json]]
        end
      end

      def handle_post_transaction(req)
        begin
          body = JSON.parse(req.body.read, symbolize_names: true)
          tenant = body[:tenant_id]
          model = body[:model_name]
          p_tokens = body[:prompt_tokens].to_i
          c_tokens = body[:completion_tokens].to_i
          
          result = @ledger.record_inference!(tenant, model, p_tokens, c_tokens)
          [201, { 'Content-Type' => 'application/json' }, [result.to_json]]
        rescue JSON::ParserError
          [400, { 'Content-Type' => 'application/json' }, [{ error: 'Invalid JSON' }.to_json]]
        rescue => e
          [400, { 'Content-Type' => 'application/json' }, [{ error: e.message }.to_json]]
        end
      end
    end
  end
end
