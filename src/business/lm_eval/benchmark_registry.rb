# @omni-layer Business | @omni-source EleutherAI/lm-evaluation-harness | @omni-lang Ruby
# @omni-description Benchmark results API: stores, compares, and reports LM
# evaluation results with leaderboard ranking.
module Omni
  module LMEval
    class BenchmarkRegistry
      def initialize
        @entries = {}
      end

      def submit(model_name:, results:, metadata: {})
        return { error: "No results" } if results.nil? || results.empty?
        entry = {
          model: model_name, results: results, metadata: metadata,
          avg_accuracy: results.values.sum { |r| r[:accuracy] || 0 } / results.size.to_f,
          submitted_at: Time.now.iso8601
        }
        @entries[model_name] = entry
        { data: entry }
      rescue StandardError => e
        { error: e.message }
      end

      def leaderboard(metric: :avg_accuracy, limit: 20)
        sorted = @entries.values.sort_by { |e| -e[:avg_accuracy] }
        {
          data: {
            rankings: sorted.first(limit).map.with_index(1) { |e, rank|
              { rank: rank, model: e[:model], score: e[:avg_accuracy], tasks: e[:results].keys }
            },
            total_models: @entries.size
          }
        }
      rescue StandardError => e
        { error: e.message }
      end

      def compare(model_a:, model_b:)
        a = @entries[model_a]; b = @entries[model_b]
        return { error: "Model not found" } unless a && b
        tasks = (a[:results].keys + b[:results].keys).uniq
        comparison = tasks.map do |task|
          acc_a = a[:results].dig(task, :accuracy) || 0
          acc_b = b[:results].dig(task, :accuracy) || 0
          { task: task, model_a: acc_a, model_b: acc_b, delta: acc_a - acc_b, winner: acc_a > acc_b ? model_a : model_b }
        end
        { data: { comparison: comparison, overall_winner: a[:avg_accuracy] > b[:avg_accuracy] ? model_a : model_b } }
      rescue StandardError => e
        { error: e.message }
      end
    end
  end
end
