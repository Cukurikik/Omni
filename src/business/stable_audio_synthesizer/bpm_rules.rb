module Omni
  module Business
    module StableAudioSynthesizer
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

      class BPMRules
        def align_audio_length(target_bpm, num_beats, sample_rate)
          if target_bpm <= 0 || num_beats <= 0 || sample_rate <= 0
            return OmniResult.new(error: StandardError.new("BPM, beats, and sample rate must be positive"))
          end

          # Audio Synthesizer Business Logic: Exact Sample Calculation
          # Ensures generated audio loops seamlessly on the beat
          
          beats_per_second = target_bpm / 60.0
          seconds_per_beat = 1.0 / beats_per_second
          
          total_seconds = num_beats * seconds_per_beat
          total_samples = (total_seconds * sample_rate).round
          
          OmniResult.new(value: { 
            total_samples: total_samples,
            exact_duration_sec: total_seconds
          })
        end
      end
    end
  end
end
