module Omni
  module Business
    module MultiModalFusionRag
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

      class ModalityRouter
        def route_query(query_string, has_image_attachment)
          if query_string.nil?
            return OmniResult.new(error: StandardError.new("Query cannot be nil"))
          end

          # Multimodal RAG Business Logic: Routing Rules
          # Determines if a query should search the Text Vector DB, Image Vector DB, or perform a Hybrid fusion
          
          if has_image_attachment
             return OmniResult.new(value: { route: "HYBRID_FUSION", strategy: "CROSS_ATTENTION" })
          end
          
          visual_keywords = ["looks like", "color of", "shape of", "picture of", "diagram"]
          
          if visual_keywords.any? { |kw| query_string.downcase.include?(kw) }
             return OmniResult.new(value: { route: "IMAGE_DB_ONLY", strategy: "TEXT_TO_IMAGE" })
          end
          
          OmniResult.new(value: { route: "TEXT_DB_ONLY", strategy: "STANDARD_RAG" })
        end
      end
    end
  end
end
