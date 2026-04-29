# OMNI Domain Layer - Diffusers Latent Shapes
module Omni
  module Domain
    module Diffusers
      class ShapeError < StandardError; end

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

      class LatentValidator
        def validate_latent_dimensions(channels, height, width)
          if channels != 4 || height % 8 != 0 || width % 8 != 0
            Result.new(error: ShapeError.new("Invalid SD latent dimensions"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
