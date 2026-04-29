# OMNI Domain Layer - KubeRay CRD Validator
module Omni
  module Domain
    module KubeRay
      class CRDError < StandardError; end

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

      class SpecValidator
        def validate_version(api_version)
          if api_version != "ray.io/v1"
            Result.new(error: CRDError.new("Unsupported Ray API version"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
