require 'tiktoken_ruby'

module Omni
  module Memory
    class Result
      attr_reader :is_success, :value, :error

      def initialize(is_success, value, error)
        @is_success = is_success
        @value = value
        @error = error
      end
      def self.success(value); new(true, value, nil); end
      def self.failure(error); new(false, nil, error); end
    end

    class ContextWindowManager
      def initialize(model_name = "gpt-4")
        begin
          @encoder = Tiktoken.encoding_for_model(model_name)
        rescue StandardError => e
          # fallback to cl100k_base for newer models
          @encoder = Tiktoken.get_encoding("cl100k_base")
        end
      end

      def fit_to_window(system_prompt, user_query, retrieved_docs, max_tokens = 4096)
        return Result.failure("Documents must be an array") unless retrieved_docs.is_a?(Array)
        
        begin
          sys_tokens = @encoder.encode(system_prompt).length
          query_tokens = @encoder.encode(user_query).length
          
          # Reserve tokens for completion
          reserved_completion = 500
          available_for_docs = max_tokens - sys_tokens - query_tokens - reserved_completion
          
          return Result.failure("Query and System prompt exceed token limit") if available_for_docs <= 0

          # Pack documents until limit is reached
          packed_docs = []
          current_tokens = 0
          
          retrieved_docs.each do |doc|
            doc_tokens = @encoder.encode(doc)
            if current_tokens + doc_tokens.length <= available_for_docs
              packed_docs << doc
              current_tokens += doc_tokens.length
            else
              # If a single doc is too large, optionally truncate it to fill the remaining space
              remaining = available_for_docs - current_tokens
              if remaining > 50
                truncated_text = @encoder.decode(doc_tokens[0...remaining])
                packed_docs << truncated_text + "... [TRUNCATED]"
              end
              break
            end
          end

          final_context = packed_docs.join("\n\n---\n\n")
          Result.success(final_context)
        rescue StandardError => e
          Result.failure("Context window management failed: #{e.message}")
        end
      end
    end
  end
end
