module Omni
  module Business
    module PaperaiMedicalIndexer
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

      class CitationRules
        def rank_paper(semantic_density_score, citation_count, year_published, current_year)
          if semantic_density_score < 0.0 || semantic_density_score > 1.0
            return OmniResult.new(error: StandardError.new("Semantic density must be between 0.0 and 1.0"))
          end

          # PaperAI Business Logic: Balancing Relevance, Authority, and Recency
          age = current_year - year_published
          
          # Recency penalty (older papers degrade in relevance unless highly cited)
          age_penalty = age > 5 ? (age - 5) * 0.05 : 0.0
          
          # Authority boost (logarithmic scaling of citations)
          authority_boost = citation_count > 0 ? Math.log10(citation_count + 1) * 0.1 : 0.0
          
          final_score = semantic_density_score + authority_boost - age_penalty
          final_score = [0.0, [final_score, 1.0].min].max # Clamp between 0 and 1
          
          verdict = final_score > 0.75 ? "HIGHLY_RECOMMENDED" : "STANDARD"

          OmniResult.new(value: { final_score: final_score, verdict: verdict })
        end
      end
    end
  end
end
