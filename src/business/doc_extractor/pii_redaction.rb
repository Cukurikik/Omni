module Omni
  module Business
    module DocExtractor
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

      class PIIRedactionPolicy
        def initialize
          # Deterministic Regex patterns for PII
          @patterns = {
            ssn: /\b\d{3}-\d{2}-\d{4}\b/,
            email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/,
            credit_card: /\b(?:\d{4}[ -]?){3}\d{4}\b/
          }
        end

        def redact_text(text)
          if text.nil? || text.empty?
            return OmniResult.new(value: text)
          end

          redacted_text = text.dup
          redaction_count = 0

          @patterns.each do |type, regex|
            redacted_text.gsub!(regex) do |match|
              redaction_count += 1
              "[" + type.to_s.upcase + " REDACTED]"
            end
          end

          OmniResult.new(value: { 
            text: redacted_text, 
            count: redaction_count 
          })
        end
      end
    end
  end
end
