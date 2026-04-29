module Omni
  module Business
    module ContextualCompressor
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

      class CompressionLimits
        def evaluate_compression_ratio(original_tokens, compressed_tokens)
          if original_tokens <= 0
            return OmniResult.new(error: StandardError.new("Original token count must be positive"))
          end
          if compressed_tokens < 0 || compressed_tokens > original_tokens
            return OmniResult.new(error: StandardError.new("Invalid compressed token count"))
          end

          # Contextual Compressor Business Logic: Quality Assurance Limits
          # Prevents over-compression which would destroy the semantic meaning of the retrieved context
          
          ratio = compressed_tokens.to_f / original_tokens.to_f
          
          if ratio < 0.20
             # Dropped more than 80% of context, likely lost critical information
             return OmniResult.new(value: { accepted: false, reason: "Compression ratio too aggressive, semantic loss likely." })
          end
          
          OmniResult.new(value: { accepted: true, ratio: ratio })
        end
      end
    end
  end
end
