# OMNI Domain Layer - MetaGPT SOPs
module Omni
  module Domain
    module MetaGPT
      class SOPError < StandardError; end

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

      class FlowValidator
        def validate_handoff(from_role, to_role)
          valid_transitions = {
            "ProductManager" => ["Architect"],
            "Architect" => ["Engineer"],
            "Engineer" => ["QA", "Engineer"],
            "QA" => ["ProductManager"]
          }
          
          if valid_transitions[from_role]&.include?(to_role)
            Result.new(value: true)
          else
            Result.new(error: SOPError.new("Invalid role transition per MetaGPT SOP"))
          end
        end
      end
    end
  end
end
