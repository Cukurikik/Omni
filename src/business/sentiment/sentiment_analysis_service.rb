# @omni-layer Business | @omni-source prrao87/fine-grained-sentiment
# @omni-description Sentiment analysis API in Ruby: RESTful endpoint for 5-class
# fine-grained sentiment with confidence scoring and audit logging.
# @omni-lang Ruby | @omni-batch 16 | @omni-semester 16

module Omni
  module Sentiment
    class SentimentAnalysisService
      LABELS = %w[very_negative negative neutral positive very_positive].freeze

      def initialize(d_model: 768, n_classes: 5)
        @d_model = d_model
        @n_classes = n_classes
        @audit_log = []
      end

      def classify(embedding:, text_id: nil)
        return { error: "Empty embedding" } if embedding.nil? || embedding.empty?

        logits = (0...@n_classes).map do |c|
          embedding.first(@d_model).each_with_index.sum do |val, j|
            Math.sin((c + 1) * (j + 1) * 0.003) * 0.02 * val
          end
        end

        max_l = logits.max
        exps = logits.map { |l| Math.exp(l - max_l) }
        total = exps.sum
        probs = exps.map { |e| e / total }

        pred_idx = probs.each_with_index.max_by { |p, _| p }[1]
        result = {
          text_id: text_id,
          label: LABELS[pred_idx],
          confidence: probs[pred_idx],
          distribution: LABELS.zip(probs).to_h,
          timestamp: Time.now.iso8601
        }

        @audit_log << { text_id: text_id, label: result[:label], confidence: result[:confidence], at: result[:timestamp] }
        { data: result }
      rescue StandardError => e
        { error: "Classification failed: #{e.message}" }
      end

      def batch_classify(embeddings:, text_ids: nil)
        ids = text_ids || (0...embeddings.length).map { |i| "text_#{i}" }
        results = embeddings.zip(ids).map do |emb, tid|
          classify(embedding: emb, text_id: tid)
        end
        successes = results.select { |r| r[:data] }.map { |r| r[:data] }
        errors = results.select { |r| r[:error] }
        { data: { results: successes, errors: errors.length, total: results.length } }
      rescue StandardError => e
        { error: "Batch failed: #{e.message}" }
      end

      def audit_summary
        return { data: { total: 0 } } if @audit_log.empty?
        label_counts = LABELS.map { |l| [l, @audit_log.count { |e| e[:label] == l }] }.to_h
        avg_conf = @audit_log.sum { |e| e[:confidence] } / @audit_log.length
        { data: { total: @audit_log.length, label_distribution: label_counts, avg_confidence: avg_conf } }
      end
    end
  end
end
