module Omni
  module Towhee
    class Result
      attr_reader :is_success, :value, :error

      def initialize(is_success, value, error)
        @is_success = is_success
        @value = value
        @error = error
      end

      def self.success(value)
        new(true, value, nil)
      end

      def self.failure(error)
        new(false, nil, error)
      end
    end

    class FeatureRouter
      def initialize(high_capacity_threshold = 100.0)
        @threshold = high_capacity_threshold
      end

      def route(feature_vector)
        return Result.failure("Vector cannot be nil or empty") if feature_vector.nil? || feature_vector.empty?
        return Result.failure("Invalid vector format") unless feature_vector.is_a?(Array)

        begin
          # Calculate vector magnitude squared to determine routing destination
          # (e.g., highly activated features go to a dedicated index)
          magnitude_sq = feature_vector.reduce(0.0) do |sum, val|
            sum + (val.to_f ** 2)
          end

          target_index = if magnitude_sq > @threshold
                           "high_capacity_index_v2"
                         else
                           "standard_index_v1"
                         end

          routing_decision = {
            target: target_index,
            magnitude: magnitude_sq,
            timestamp: Time.now.utc.iso8601
          }

          Result.success(routing_decision)
        rescue StandardError => e
          Result.failure("Routing calculation error: #{e.message}")
        end
      end
    end
  end
end
