# OMNI Domain Layer - FastChat Protocol Rules
module Omni
  module Domain
    module FastChat
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
        def validate_role(role)
          allowed_roles = ["user", "assistant", "system"]
          if !allowed_roles.include?(role)
            Result.new(error: ProtocolError.new("Invalid role type"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
