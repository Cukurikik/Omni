module Omni
  module Business
    module KongGateway
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

      class PluginPipeline
        def validate_plugin_execution_order(plugins)
          if plugins.nil? || !plugins.is_a?(Array)
            return OmniResult.new(error: StandardError.new("Plugins must be provided as an array"))
          end

          # Kong Business rules: Authentication MUST run before Rate Limiting.
          auth_idx = plugins.index { |p| p.start_with?('auth-') }
          rate_limit_idx = plugins.index { |p| p == 'rate-limiting' }

          if auth_idx && rate_limit_idx && auth_idx > rate_limit_idx
            return OmniResult.new(error: StandardError.new("Security violation: Authentication plugin must execute BEFORE Rate Limiting plugin"))
          end

          # Transformation should ideally run after security checks
          transform_idx = plugins.index { |p| p == 'request-transformer' }
          if transform_idx && auth_idx && transform_idx < auth_idx
            return OmniResult.new(error: StandardError.new("Security violation: Request transformation must occur AFTER Authentication"))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
