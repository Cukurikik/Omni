# omni_rest_router.rb — Main REST API Router
# Layer: Interface / Ruby
#
# Lightweight HTTP router acting as the user-facing REST gateway,
# routing requests to internal gRPC or Elixir services.

require 'json'

module Omni
  module Interface
    class RestRouter
      # Simplified Rack-compatible routing
      def call(env)
        req = Rack::Request.new(env)
        
        case req.path
        when '/api/v1/health'
          handle_health(req)
        when '/api/v1/completions'
          handle_completions(req)
        else
          not_found
        end
      end

      private

      def handle_health(_req)
        response(200, { status: 'healthy', version: '3.0.0-OMNI-NEXUS' })
      end

      def handle_completions(req)
        return method_not_allowed unless req.post?
        
        begin
          body = JSON.parse(req.body.read, symbolize_names: true)
          
          # Validate request
          return bad_request("Missing prompt") unless body[:prompt]
          
          # In production, forwards to Go gRPC or Elixir Gateway
          # response_data = grpc_client.generate_completion(...)
          
          mock_data = {
            id: "chatcmpl-#{SecureRandom.hex(8)}",
            object: "chat.completion",
            created: Time.now.to_i,
            model: body[:model] || "omni-default",
            choices: [
              {
                message: {
                  role: "assistant",
                  content: "This is a REST-routed OMNI completion."
                },
                finish_reason: "stop"
              }
            ]
          }
          
          response(200, mock_data)
        rescue JSON::ParserError
          bad_request("Invalid JSON body")
        end
      end

      def response(status, body_hash)
        [
          status,
          { 'Content-Type' => 'application/json' },
          [body_hash.to_json]
        ]
      end

      def not_found
        response(404, { error: 'Endpoint not found' })
      end
      
      def bad_request(msg)
        response(400, { error: msg })
      end

      def method_not_allowed
        response(405, { error: 'Method not allowed' })
      end
    end
  end
end

# Mock Rack constant for compilation/syntax checking
module Rack
  class Request
    def initialize(env); @env = env; end
    def path; @env['PATH_INFO']; end
    def post?; @env['REQUEST_METHOD'] == 'POST'; end
    def body; StringIO.new(@env['rack.input'] || '{}'); end
  end
end
