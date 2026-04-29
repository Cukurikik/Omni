module Omni
  module Business
    module AudioSemanticSearch
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

      class TranscriptionFallback
        def evaluate_audio_quality(snr_db, mfcc_confidence)
          # Audio RAG Business Logic: Fallback Routing
          # If the audio signal-to-noise ratio is too poor for direct MFCC semantic search,
          # fallback to Whisper transcription -> Text RAG
          
          if snr_db < 5.0 || mfcc_confidence < 0.4
             return OmniResult.new(value: { 
               route: "TRANSCRIPTION_FALLBACK", 
               reason: "Poor audio quality detected, standard semantic audio search will fail." 
             })
          end
          
          OmniResult.new(value: { route: "DIRECT_AUDIO_SEARCH", reason: "Audio quality sufficient for MFCC matching" })
        end
      end
    end
  end
end
