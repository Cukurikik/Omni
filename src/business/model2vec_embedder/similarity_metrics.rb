module Omni
  module Business
    module Model2VecEmbedder
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

      class SimilarityMetrics
        def initialize(min_similarity_threshold: 0.85)
          @threshold = min_similarity_threshold
        end

        # Deterministic Cosine Similarity Math
        def compute_cosine_similarity(vec_a, vec_b)
          if vec_a.nil? || vec_b.nil? || vec_a.length != vec_b.length || vec_a.empty?
            return OmniResult.new(error: StandardError.new("Invalid vectors for similarity computation"))
          end

          dot_product = 0.0
          norm_a = 0.0
          norm_b = 0.0

          vec_a.zip(vec_b).each do |a, b|
            dot_product += a * b
            norm_a += a * a
            norm_b += b * b
          end

          norm_a = Math.sqrt(norm_a)
          norm_b = Math.sqrt(norm_b)

          if norm_a == 0.0 || norm_b == 0.0
            return OmniResult.new(error: StandardError.new("Zero norm vector detected"))
          end

          similarity = dot_product / (norm_a * norm_b)

          # Business Rules Validation
          if similarity < @threshold
            return OmniResult.new(value: { similarity: similarity, match: false, reason: "Below threshold" })
          end

          OmniResult.new(value: { similarity: similarity, match: true })
        end
      end
    end
  end
end
