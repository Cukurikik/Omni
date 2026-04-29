module Omni
  module AutoML
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

    class ModelEvaluator
      def evaluate(model_id, metrics)
        return Result.failure("Invalid model_id: must be present") if model_id.nil? || model_id.strip.empty?
        return Result.failure("Metrics payload is nil") if metrics.nil?

        begin
          accuracy = metrics.fetch(:accuracy, 0.0).to_f
          latency_ms = metrics.fetch(:latency_ms, 1.0).to_f
          memory_mb = metrics.fetch(:memory_mb, 1.0).to_f
          
          return Result.failure("Latency cannot be zero or negative") if latency_ms <= 0

          # Multi-objective optimization score
          # High accuracy is good. High latency/memory is bad.
          # Equation: Score = (Accuracy^2) / (log10(latency_ms + 10) * log10(memory_mb + 10))
          
          acc_sq = accuracy ** 2
          lat_pen = Math.log10(latency_ms + 10)
          mem_pen = Math.log10(memory_mb + 10)
          
          score = acc_sq / (lat_pen * mem_pen)
          
          Result.success(score.round(4))
        rescue KeyError => e
          Result.failure("Missing essential metric: #{e.message}")
        rescue StandardError => e
          Result.failure("Evaluation fault: #{e.message}")
        end
      end
    end
  end
end
