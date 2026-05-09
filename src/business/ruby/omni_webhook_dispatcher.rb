# OMNI Business — Webhook Dispatcher
# Dispatches async events (like fine-tuning completion) to tenant webhooks

require 'net/http'
require 'uri'
require 'json'
require 'logger'

module OmniWebhooks
  class Dispatcher
    def initialize
      @logger = Logger.new(STDOUT)
    end

    def dispatch(url_string, event_type, payload)
      uri = URI.parse(url_string)
      request = Net::HTTP::Post.new(uri)
      request.content_type = "application/json"
      request["X-Omni-Event"] = event_type
      
      body = {
        event: event_type,
        timestamp: Time.now.utc.iso8601,
        data: payload
      }
      request.body = JSON.dump(body)

      @logger.info("Dispatching #{event_type} to #{url_string}")
      
      # In production, use async queue (Sidekiq/RabbitMQ) for HTTP calls
      # response = Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == 'https') do |http|
      #   http.request(request)
      # end
      # @logger.info("Response: #{response.code}")
    end
  end
end
