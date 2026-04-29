# OMNI Domain Layer - CAME Config
module Omni
  module Domain
    module CAME
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

      class Configuration
        def validate_params(learning_rate, beta1, beta2)
          if learning_rate <= 0 || beta1 < 0 || beta2 < 0 || beta1 >= 1 || beta2 >= 1
            Result.new(error: ConfigError.new("Invalid CAME parameters"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
