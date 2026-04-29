module Omni
  module Business
    module DoclingExtractor
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

      class ExtractionRules
        def initialize(min_confidence: 0.85)
          @min_confidence = min_confidence
        end

        def validate_extraction(raw_text, confidence)
          if raw_text.nil? || raw_text.strip.empty?
            return OmniResult.new(error: StandardError.new("Extracted text is empty"))
          end

          # Business Logic: Enforce confidence thresholds and sanitize PI/junk characters
          if confidence < @min_confidence
            return OmniResult.new(error: StandardError.new("Confidence score #{confidence} is below threshold #{@min_confidence}"))
          end

          # Deterministic sanitization
          sanitized = raw_text.gsub(/[\x00-\x1F\x7F]/, '').strip
          
          OmniResult.new(value: sanitized)
        end
      end
    end
  end
end
