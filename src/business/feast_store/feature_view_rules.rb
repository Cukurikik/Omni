module Omni
  module Business
    module FeastStore
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

      class FeatureViewRules
        def validate_feature_view(name, entities, schema)
          if name.nil? || name.strip.empty?
            return OmniResult.new(error: StandardError.new("FeatureView name cannot be empty"))
          end

          unless name.match?(/^[a-z0-9_]+$/)
            return OmniResult.new(error: StandardError.new("FeatureView name must be lowercase alphanumeric and underscores only"))
          end

          if entities.nil? || entities.empty?
            return OmniResult.new(error: StandardError.new("FeatureView must have at least one entity mapping"))
          end

          if schema.nil? || schema.empty?
            return OmniResult.new(error: StandardError.new("FeatureView must define a schema"))
          end

          # Deterministic strict schema validation
          allowed_types = ["INT64", "FLOAT64", "STRING", "BYTES", "BOOL"]
          schema.each do |col, type|
            unless allowed_types.include?(type.upcase)
              return OmniResult.new(error: StandardError.new("Unsupported Feast schema type: #{type}"))
            end
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
