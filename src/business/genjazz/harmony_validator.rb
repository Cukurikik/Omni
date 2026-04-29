require_relative '../../bridge/omni_result'

module OmniBusiness
  module GenJazz
    class HarmonyValidator
      # OMNI BUSINESS LAYER: Generative Jazz
      # Validates generated sequences against basic jazz harmony rules (e.g. scale degrees).

      # C Dorian scale MIDI notes (C4 = 60)
      DORIAN_C = [60, 62, 63, 65, 67, 69, 70, 72, 74, 75, 77, 79, 81, 82]

      def validate_sequence(midi_sequence)
        begin
          return OmniResult::Err.new("Empty sequence") if midi_sequence.empty?

          out_of_scale_count = 0
          
          midi_sequence.each do |note|
            # Simple modulo 12 check against Dorian mode intervals (0, 2, 3, 5, 7, 9, 10)
            normalized_pitch = note % 12
            unless [0, 2, 3, 5, 7, 9, 10].include?(normalized_pitch)
              out_of_scale_count += 1
            end
          end

          dissonance_ratio = out_of_scale_count.to_f / midi_sequence.length

          # If dissonance is too high, it might just be noise, not 'jazz'
          is_valid = dissonance_ratio < 0.4 

          OmniResult::Ok.new({
            valid: is_valid,
            dissonance_ratio: dissonance_ratio,
            notes_checked: midi_sequence.length
          })
        rescue => e
          OmniResult::Err.new("Harmony validation failed: #{e.message}")
        end
      end
    end
  end
end
