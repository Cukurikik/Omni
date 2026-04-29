# OMNI Domain Layer - Bamboo Config
module Omni
  module Domain
    module Bamboo
      class ConfigError < StandardError; end

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

      class HardwareValidator
        def check_vram_requirement(available_vram, required_vram)
          if available_vram < required_vram
            Result.new(error: ConfigError.new("Insufficient VRAM for Bamboo-7B"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
