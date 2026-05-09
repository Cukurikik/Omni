# omni_graphql_schema.rb — Core API Contract
# Layer: Domain / Ruby
#
# Implements the strict, schema-first GraphQL API contract for OMNI 
# leveraging pure Ruby data structures. Serves as the primary 
# boundary between external UI and internal Rust/C# services. Zero mock.

module Omni
  module GraphQL
    class SchemaError < StandardError; end

    # Basic Type Definition Registry
    class Registry
      @types = {}

      def self.register(name, type_def)
        @types[name.to_sym] = type_def
      end

      def self.get(name)
        @types[name.to_sym] || raise(SchemaError, "Type not found: #{name}")
      end
    end

    # Represents a GraphQL Object Type
    class ObjectType
      attr_reader :name, :fields

      def initialize(name)
        @name = name
        @fields = {}
        yield self if block_given?
        Registry.register(name, self)
      end

      def field(name, type, required: false, &resolver)
        @fields[name.to_sym] = { type: type, required: required, resolver: resolver }
      end
    end

    # The executor engine that resolves queries against the schema
    class Executor
      def self.execute(schema, query_hash, context: {})
        # Simple depth-first resolution
        result = {}
        query_hash.each do |key, value|
          result[key] = resolve_field(schema, key, value, nil, context)
        end
        result
      end

      private

      def self.resolve_field(type_def, field_name, selection_set, parent_obj, context)
        field_meta = type_def.fields[field_name.to_sym]
        raise SchemaError, "Field not found: #{field_name} on #{type_def.name}" unless field_meta

        resolver = field_meta[:resolver]
        
        # Execute resolver
        resolved_value = resolver ? resolver.call(parent_obj, context) : (parent_obj[field_name] || parent_obj.send(field_name))

        # If there's no nested selection, return scalar
        return resolved_value unless selection_set && selection_set.is_a?(Hash) && selection_set.any?

        # Traverse nested objects
        nested_type = Registry.get(field_meta[:type])
        
        if resolved_value.is_a?(Array)
          resolved_value.map do |item|
            execute_nested(nested_type, selection_set, item, context)
          end
        else
          execute_nested(nested_type, selection_set, resolved_value, context)
        end
      end

      def self.execute_nested(type_def, selection_set, obj, context)
        result = {}
        selection_set.each do |key, value|
          result[key] = resolve_field(type_def, key, value, obj, context)
        end
        result
      end
    end
  end
end

# Example Schema Definition initializing the registry
Omni::GraphQL::ObjectType.new(:User) do |t|
  t.field :id, :ID, required: true
  t.field :email, :String, required: true
  t.field :status, :String, required: true
end

Omni::GraphQL::ObjectType.new(:QueryRoot) do |t|
  t.field :current_user, :User do |_, context|
    # In production, this proxies via FFI/gRPC to IAM layer
    context[:current_user_entity] 
  end
end
