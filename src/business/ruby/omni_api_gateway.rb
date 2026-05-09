# OMNI Business — Ruby API Gateway
# Handles request normalization and rate limiting

require 'json'
require 'logger'

module OmniGateway
  class Router
    def initialize
      @logger = Logger.new(STDOUT)
      @rate_limits = Hash.new(0)
    end

    def call(env)
      req = Rack::Request.new(env)
      client_ip = req.ip
      
      # Rate Limiting
      if @rate_limits[client_ip] > 100
        @logger.warn("Rate limit exceeded for #{client_ip}")
        return [429, { 'Content-Type' => 'application/json' }, [{ error: "Rate limit exceeded" }.to_json]]
      end
      
      @rate_limits[client_ip] += 1
      
      case req.path
      when '/v1/completions'
        handle_completions(req)
      else
        [404, { 'Content-Type' => 'application/json' }, [{ error: "Endpoint not found" }.to_json]]
      end
    end

    private

    def handle_completions(req)
      body = JSON.parse(req.body.read) rescue {}
      @logger.info("Routing completion request to inference engine: #{body['model']}")
      
      # Mock response for architectural design
      [200, { 'Content-Type' => 'application/json' }, [{ id: "omni-123", choices: [{text: "Hello from Omni"}] }.to_json]]
    end
  end
end
