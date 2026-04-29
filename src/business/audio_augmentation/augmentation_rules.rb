module Omni
  module Business
    module AudioAugmentation
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

      class AugmentationRules
        def initialize(max_semitones: 12.0)
          @max_semitones = max_semitones
        end

        def validate_pitch_shift(semitones: Float)
          if semitones.abs > @max_semitones
            return OmniResult.new(error: StandardError.new("Pitch shift exceeds maximum allowed semitones (#{@max_semitones})"))
          end

          # Business logic: Determine if shift causes severe distortion risk
          distortion_risk = semitones.abs > 6.0 ? "HIGH" : "LOW"

          OmniResult.new(value: { 
            status: "APPROVED",
            distortion_risk: distortion_risk,
            shift_factor: (2.0 ** (semitones / 12.0)).round(4)
          })
        end
      end
    end
  end
end
