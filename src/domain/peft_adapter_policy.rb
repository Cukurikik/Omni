# OMNI Domain Layer - PEFT Adapter Policy
module Omni
  module Domain
    module PEFT
      class AdapterError < StandardError; end

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

      class MergerValidator
        def validate_adapter_compatibility(base_arch, adapter_arch)
          if base_arch != adapter_arch
            Result.new(error: AdapterError.new("Base model and adapter architectures must match"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
