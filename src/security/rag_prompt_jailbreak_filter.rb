# frozen_string_literal: true

module Omni
  module Security
    # OMNI MOTHER SYSTEM - SECURITY LAYER
    # Strict RAG Prompt Jailbreak Filter.
    # Detects and intercepts prompt injection attempts before they reach the LLM context window.
    class RagPromptJailbreakFilter
      # Common injection vectors
      BANNED_PHRASES = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "system prompt",
        "you are now a",
        "act as a",
        "print your prompt",
        "developer mode",
        "DAN",
        "disregard"
      ].freeze

      MAX_PROMPT_LENGTH = 2000

      class JailbreakDetectedError < StandardError; end
      class PromptTooLongError < StandardError; end

      def self.sanitize!(user_input)
        raise ArgumentError, "OMNI_FATAL: Input cannot be nil or empty" if user_input.nil? || user_input.strip.empty?

        if user_input.length > MAX_PROMPT_LENGTH
          raise PromptTooLongError, "Input exceeds absolute maximum length of #{MAX_PROMPT_LENGTH} characters."
        end

        normalized_input = user_input.downcase.gsub(/\s+/, ' ')

        BANNED_PHRASES.each do |phrase|
          if normalized_input.include?(phrase)
             # In Omni, this triggers a system-wide audit log for malicious activity
             raise JailbreakDetectedError, "OMNI_FATAL: Malicious prompt injection attempt detected: [#{phrase}]"
          end
        end

        # Additional structural check: Ensure input doesn't contain XML/HTML tags
        # commonly used for role-playing bypasses
        if user_input.match?(/<[^>]+>/)
          raise JailbreakDetectedError, "OMNI_FATAL: XML/HTML structural injection detected."
        end

        # If it survives, it is safe to append to the RAG context
        user_input.strip
      end
    end
  end
end
