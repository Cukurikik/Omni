require_relative '../../bridge/omni_result'

module OmniBusiness
  module AILiterature
    class CitationGraph
      # OMNI BUSINESS LAYER: Citation Network
      # Builds and ranks a directed graph of paper citations using PageRank logic.

      def initialize
        @nodes = {}
        @edges = Hash.new { |h, k| h[k] = [] }
      end

      def add_citation(source_paper_id, cited_paper_id)
        begin
          @nodes[source_paper_id] ||= { score: 1.0 }
          @nodes[cited_paper_id] ||= { score: 1.0 }
          
          @edges[source_paper_id] << cited_paper_id
          
          OmniResult::Ok.new(true)
        rescue => e
          OmniResult::Err.new("Graph construction failed: #{e.message}")
        end
      end

      def compute_pagerank(iterations = 10, damping = 0.85)
        begin
          return OmniResult::Ok.new({}) if @nodes.empty?

          n = @nodes.size
          iterations.times do
            new_scores = {}
            @nodes.keys.each { |k| new_scores[k] = (1.0 - damping) / n }

            @edges.each do |source, targets|
              contribution = damping * (@nodes[source][:score] / targets.size)
              targets.each do |t|
                new_scores[t] += contribution
              end
            end

            new_scores.each { |k, v| @nodes[k][:score] = v }
          end

          # Return top 10 most influential papers
          top_papers = @nodes.sort_by { |_, v| -v[:score] }.take(10).to_h
          OmniResult::Ok.new(top_papers)
        rescue => e
          OmniResult::Err.new("PageRank compute failed: #{e.message}")
        end
      end
    end
  end
end
