# OMNI Domain Layer - MCP Protocol
module Omni
  module Domain
    module MCP
      class ProtocolError < StandardError; end

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

      class MessageValidator
        def validate_payload(payload)
          if payload.nil? || !payload.is_a?(Hash)
            Result.new(error: ProtocolError.new("Payload must be a valid Hash"))
          elsif !payload.key?(:type)
            Result.new(error: ProtocolError.new("Payload missing type field"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
