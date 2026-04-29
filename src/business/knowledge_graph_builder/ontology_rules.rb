module Omni
  module Business
    module KnowledgeGraphBuilder
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class OntologyRules
        def validate_triplet(subject_type, predicate, object_type)
          if subject_type.nil? || predicate.nil? || object_type.nil?
            return OmniResult.new(error: StandardError.new("Triplet components cannot be nil"))
          end

          # Knowledge Graph Business Logic: Strict Ontology Enforcement
          # Prevents nonsensical relationships from polluting the Graph RAG
          
          valid_relations = {
            "PERSON" => ["BORN_IN", "WORKS_FOR", "OWNS"],
            "COMPANY" => ["ACQUIRES", "PRODUCES", "LOCATED_IN"],
            "LOCATION" => ["PART_OF", "CONTAINS"]
          }
          
          allowed_predicates = valid_relations[subject_type]
          
          if allowed_predicates && allowed_predicates.include?(predicate)
             return OmniResult.new(value: { valid: true, reason: "Adheres to defined ontology" })
          end
          
          OmniResult.new(value: { valid: false, reason: "Predicate #{predicate} invalid for subject type #{subject_type}" })
        end
      end
    end
  end
end
