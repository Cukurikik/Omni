#=============================================================================
# OMNI DOMAIN LAYER — PATENT SEARCH RESOLVER (RUBY)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: GraphQL Ruby Resolver for querying AI Patents via Julia compute.
#=============================================================================

require 'omni_bridge/domain'

module Omni
  module Domain
    module Patents
      class PatentSearchResolver
        
        # OMNI IDIOM: Domain logic resolving GraphQL Queries
        def self.search(query_text:, top_k: 10)
          # 1. Embed query text via Python NLP layer
          embed_res = Omni::Bridge::EventLoop.call_sync("compute.nlp.embed_text", {text: query_text})
          return [] unless embed_res.success?
          
          query_vector = embed_res.data["vector"]

          # 2. Search patent vectors via Julia Compute layer (cosine_similarity_simd)
          search_res = Omni::Bridge::EventLoop.call_sync("compute.nlp.patent_search", {
            vector: query_vector,
            limit: top_k
          })
          
          return [] unless search_res.success?

          # 3. Format to GraphQL Response Type
          search_res.data["results"].map do |res|
            {
              id: res["patent_id"],
              similarity: res["score"],
              title: res["metadata"]["title"] || "Unknown Title"
            }
          end
        end
        
      end
    end
  end
end
