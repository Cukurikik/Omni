# OMNI Domain Layer - ChatTTS Prosody
module Omni
  module Domain
    module ChatTTS
      class ProsodyError < StandardError; end

      class Result
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class SpeechValidator
        def validate_speech_rate(rate)
          if rate < 0.5 || rate > 2.0
            Result.new(error: ProsodyError.new("Speech rate out of bounds for natural prosody"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
