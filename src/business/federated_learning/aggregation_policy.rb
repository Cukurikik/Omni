module Omni
  module Business
    module FederatedLearning
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class AggregationPolicy
        def initialize(min_clients: 3, max_loss_threshold: 2.0)
          @min_clients = min_clients
          @max_loss_threshold = max_loss_threshold
        end

        def validate_round(client_reports)
          if client_reports.nil? || client_reports.empty?
            return OmniResult.new(error: StandardError.new("Empty client reports"))
          end

          # Filter out stragglers or malicious actors based on deterministic bounds
          valid_clients = []
          
          client_reports.each do |report|
            if report[:loss] <= @max_loss_threshold && report[:samples_trained] > 0
              valid_clients << report
            end
          end

          if valid_clients.length < @min_clients
            return OmniResult.new(error: StandardError.new("Not enough valid clients to aggregate. Required: #{@min_clients}, Found: #{valid_clients.length}"))
          end

          OmniResult.new(value: { valid_reports: valid_clients, count: valid_clients.length })
        end
      end
    end
  end
end
