# omni_telemetry_sink.rb — Telemetry Aggregator
# Layer: Domain / Ruby
#
# Receives performance and latency metrics from the eBPF kernel layer
# and aggregates them into time-series logs for the UI Dashboard.

require 'json'
require 'logger'
require 'socket'

module Omni
  module Analytics
    class TelemetrySink
      def initialize(port = 9001)
        @logger = Logger.new(STDOUT)
        @logger.level = Logger::INFO
        @port = port
        
        # In-memory aggregation buffer
        @latency_buffer = []
        @lock = Mutex.new
      end

      def start_listener
        Thread.new do
          # Listen for UDP packets from the eBPF user-space agent
          socket = UDPSocket.new
          socket.bind('127.0.0.1', @port)
          
          @logger.info("Telemetry Sink listening on UDP 127.0.0.1:#{@port}")
          
          loop do
            data, _addr = socket.recvfrom(1024)
            process_payload(data)
          end
        end
      end

      def process_payload(json_str)
        begin
          event = JSON.parse(json_str, symbolize_names: true)
          
          if event[:type] == 'network_latency'
            @lock.synchronize do
              @latency_buffer << event[:latency_ns]
              # Keep buffer from growing infinitely
              @latency_buffer.shift if @latency_buffer.size > 1000
            end
          end
        rescue JSON::ParserError
          @logger.warn("Received malformed telemetry payload")
        end
      end

      def get_average_latency_ms
        @lock.synchronize do
          return 0.0 if @latency_buffer.empty?
          avg_ns = @latency_buffer.sum.to_f / @latency_buffer.size
          (avg_ns / 1_000_000.0).round(3)
        end
      end
      
      def get_dashboard_metrics
        {
          networkLatency: get_average_latency_ms,
          timestamp: Time.now.utc.to_s
        }
      end
    end
  end
end
