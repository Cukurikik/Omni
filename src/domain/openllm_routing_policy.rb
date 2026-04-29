# OMNI Domain Layer - OpenLLM Routing Policy
module Omni
  module Domain
    module OpenLLM
      class RouteError < StandardError; end

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

      class AccessValidator
        def validate_model_access(api_key, requested_model)
          if api_key.nil? || api_key.empty?
            Result.new(error: RouteError.new("API Key required for OpenLLM endpoint"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
