# OMNI Domain Layer - xTuring Personalization
module Omni
  module Domain
    module XTuring
      class PersonalizeError < StandardError; end

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

      class StyleValidator
        def validate_tone(tone)
          valid_tones = ["professional", "casual", "sarcastic", "helpful"]
          if !valid_tones.include?(tone)
            Result.new(error: PersonalizeError.new("Unsupported personality tone"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
