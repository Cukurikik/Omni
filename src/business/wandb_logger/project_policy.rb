module Omni
  module Business
    module WandBLogger
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

      class ProjectPolicy
        def validate_experiment_config(project_name, api_key)
          if project_name.nil? || project_name.strip.empty?
            return OmniResult.new(error: StandardError.new("Project name is required"))
          end

          # Enforce naming constraints for URL safety
          unless project_name.match?(/^[a-zA-Z0-9_-]+$/)
            return OmniResult.new(error: StandardError.new("Project name can only contain alphanumeric characters, underscores, and hyphens"))
          end

          if api_key.nil? || api_key.length != 40
            return OmniResult.new(error: StandardError.new("API key must be exactly 40 characters"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
