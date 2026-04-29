require 'securerandom'

module Omni
  module Prompting
    class Result
      attr_reader :data, :error

      def initialize(data: nil, error: nil)
        @data = data
        @error = error
      end

      def ok?
        @error.nil?
      end

      def unwrap
        raise "Unwrap failed: #{@error}" unless ok?
        @data
      end
    end

    class ExperimentTracker
      def initialize
        @experiments = {} # id => data
        @results = {}     # exp_id => [metrics]
      end

      def create_experiment(name, templates_hash)
        begin
          if templates_hash.empty?
            return Result.new(error: "Must provide at least one template")
          end

          exp_id = SecureRandom.uuid
          
          @experiments[exp_id] = {
            name: name,
            templates: templates_hash, # { variant_a: "prompt...", variant_b: "prompt..." }
            created_at: Time.now.utc.to_i,
            status: "active"
          }
          
          @results[exp_id] = []

          Result.new(data: exp_id)
        rescue StandardError => e
          Result.new(error: "Failed to create experiment: #{e.message}")
        end
      end

      def log_inference(exp_id, variant_key, latency_ms, score)
        begin
          exp = @experiments[exp_id]
          return Result.new(error: "Experiment not found") unless exp
          return Result.new(error: "Experiment inactive") if exp[:status] != "active"
          return Result.new(error: "Invalid variant") unless exp[:templates].key?(variant_key)

          record = {
            variant: variant_key,
            latency_ms: latency_ms,
            score: score, # Extrinsic evaluation score (e.g., ROUGE, BLEU, or Human)
            timestamp: Time.now.utc.to_i
          }

          @results[exp_id] << record
          Result.new(data: true)
        rescue StandardError => e
          Result.new(error: "Logging failed: #{e.message}")
        end
      end

      def calculate_ab_winner(exp_id)
        begin
          records = @results[exp_id]
          return Result.new(error: "No results logged") if records.nil? || records.empty?

          aggregated = {}
          records.each do |r|
            v = r[:variant]
            aggregated[v] ||= { sum_score: 0.0, count: 0, sum_latency: 0.0 }
            aggregated[v][:sum_score] += r[:score]
            aggregated[v][:sum_latency] += r[:latency_ms]
            aggregated[v][:count] += 1
          end

          metrics = aggregated.map do |k, v|
            {
              variant: k,
              avg_score: v[:sum_score] / v[:count],
              avg_latency: v[:sum_latency] / v[:count],
              sample_size: v[:count]
            }
          end

          winner = metrics.max_by { |m| m[:avg_score] }
          Result.new(data: { winner: winner[:variant], metrics: metrics })
        rescue StandardError => e
          Result.new(error: "Calculation failed: #{e.message}")
        end
      end
    end
  end
end
