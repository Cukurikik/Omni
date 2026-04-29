module Omni
  module Business
    module FeatureStore
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

      class SchemaValidation
        def initialize
          @allowed_types = ["int", "float", "string", "boolean"]
        end

        def validate_feature_schema(schema_def)
          if schema_def.nil? || schema_def.empty?
            return OmniResult.new(error: StandardError.new("Schema definition cannot be empty"))
          end

          unless schema_def.key?(:feature_name) && schema_def.key?(:type)
            return OmniResult.new(error: StandardError.new("Schema missing required fields"))
          end

          # Business Rule: strict typing support
          unless @allowed_types.include?(schema_def[:type])
            return OmniResult.new(error: StandardError.new("Unsupported feature type: #{schema_def[:type]}"))
          end

          # Business Rule: Entity key validation
          if schema_def[:entity_keys].nil? || schema_def[:entity_keys].empty?
            return OmniResult.new(error: StandardError.new("Feature must belong to at least one entity key"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
