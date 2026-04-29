module Omni
  module DataScienceQA
    class QAEngine
      def initialize(embeddings_client)
        @embeddings = embeddings_client
        @index = [] # Represents Vector DB
      end

      # Ingest Question-Answer pairs
      def ingest(question, answer)
        vector = @embeddings.embed(question)
        @index << { q: question, a: answer, v: vector }
      end

      # Find most relevant answer
      def search(query)
        query_vector = @embeddings.embed(query)
        
        best_match = @index.max_by do |doc|
          cosine_similarity(query_vector, doc[:v])
        end

        best_match ? best_match[:a] : "No relevant answer found."
      end

      private

      def cosine_similarity(v1, v2)
        dot = v1.zip(v2).map { |a, b| a * b }.sum
        mag1 = Math.sqrt(v1.map { |x| x**2 }.sum)
        mag2 = Math.sqrt(v2.map { |x| x**2 }.sum)
        dot / (mag1 * mag2)
      end
    end
  end
end
