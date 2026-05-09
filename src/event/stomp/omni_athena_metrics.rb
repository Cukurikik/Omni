# OMNI Framework - Ruby STOMP Client for AthenaOS Metrics
# Routes system metrics via STOMP protocol to monitoring sinks

require 'stomp'
require 'json'

module Omni
  class AthenaMetricsPublisher
    def initialize
      @client = Stomp::Client.new('omni_agent', 'secret', 'omni-activemq', 61613)
      puts "OMNI STOMP: Connected to broker."
    end

    def publish_metrics(node_id, cpu_load, ram_usage)
      payload = {
        node_id: node_id,
        cpu_load: cpu_load,
        ram_usage: ram_usage,
        timestamp: Time.now.utc.iso8601
      }
      
      # Publish to queue
      @client.publish('/queue/omni.athena.metrics', payload.to_json, { 'persistent' => 'true' })
      puts "OMNI STOMP: Published metrics for #{node_id}."
    end
    
    def disconnect
      @client.close
    end
  end
end

# Usage:
# publisher = Omni::AthenaMetricsPublisher.new
# publisher.publish_metrics("athena-worker-01", 85.2, 4096)
# publisher.disconnect
