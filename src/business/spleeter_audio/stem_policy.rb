module Omni
  module Business
    module SpleeterAudio
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

      class StemPolicy
        ALLOWED_STEMS = [2, 4, 5].freeze

        def validate_stem_request(num_stems, sample_rate)
          unless ALLOWED_STEMS.include?(num_stems)
            return OmniResult.new(error: StandardError.new("Invalid stem count. Supported: 2 (vocals/accomp), 4 (vocals/drums/bass/other), 5 (+piano)"))
          end

          if sample_rate != 44100 && sample_rate != 48000
            return OmniResult.new(error: StandardError.new("Strictly supporting 44.1kHz or 48.0kHz sample rates for deterministic model inputs"))
          end

          OmniResult.new(value: { validated: true, stems: num_stems })
        end
      end
    end
  end
end
