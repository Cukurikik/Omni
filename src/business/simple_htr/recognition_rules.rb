module Omni
  module Business
    module SimpleHTR
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

      class RecognitionRules
        def initialize(min_confidence: 0.6)
          @min_confidence = min_confidence
        end

        def validate_transcription(transcription: String, confidence: Float)
          if transcription.nil? || transcription.empty?
            return OmniResult.new(error: StandardError.new("Transcription cannot be empty"))
          end

          if confidence < 0.0 || confidence > 1.0
            return OmniResult.new(error: StandardError.new("Confidence must be between 0 and 1"))
          end

          # Business Logic: Reject low confidence or sanitize text
          if confidence < @min_confidence
            return OmniResult.new(value: { status: "REJECTED", sanitized: "" })
          end

          # Deterministic sanitization: remove weird characters
          sanitized = transcription.gsub(/[^a-zA-Z0-9\s.,?!']/, '')

          OmniResult.new(value: { status: "ACCEPTED", sanitized: sanitized })
        end
      end
    end
  end
end
