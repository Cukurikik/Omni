module Omni
  module Business
    module AwesomeRagOrchestrator
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

      class ChunkingRules
        def validate_semantic_chunk(token_count, overlap_count, embedding_model_limit)
          if token_count <= 0 || overlap_count < 0 || embedding_model_limit <= 0
            return OmniResult.new(error: StandardError.new("Invalid chunk parameters"))
          end

          # RAG Business Logic: Optimal Semantic Chunking
          if token_count > embedding_model_limit
            return OmniResult.new(value: { 
              status: "REJECTED", 
              reason: "Chunk exceeds embedding model absolute limit",
              suggested_action: "SPLIT_CHUNK" 
            })
          end

          if overlap_count > token_count * 0.5
            return OmniResult.new(value: {
              status: "WARNING",
              reason: "Overlap is excessively high (>50%), wasting vector DB space",
              suggested_action: "REDUCE_OVERLAP"
            })
          end

          OmniResult.new(value: { status: "APPROVED", suggested_action: "PROCEED_TO_EMBEDDING" })
        end
      end
    end
  end
end
