# ===========================================================================
# OMNI DSL ENGINE (SEMESTER 3 — BATCH 38.5)
# ===========================================================================
# Absorbed From  : Rails routes DSL + Sinatra + RSpec + Rake
# Logic Inherited: Ruby / Business Layer (Metaprogramming DSL Builder)
# ===========================================================================
#
# By studying Rails and Sinatra, Mother learned Ruby's DSL superpowers:
#   1. instance_eval shifts self context into a block
#   2. method_missing enables fluent, dynamic APIs
#   3. define_method creates methods at runtime
#   4. class_eval opens classes for dynamic modification
#   5. Blocks as configuration closures (Builder pattern)

# frozen_string_literal: true

module Omni
  module DSL
    # ================================================================
    # PART 1: Route DSL (Sinatra/Rails-inspired)
    # ================================================================

    class RouteDefinition
      attr_reader :method, :path, :handler, :middleware, :constraints

      def initialize(method, path, handler, middleware: [], constraints: {})
        @method = method.to_s.upcase.freeze
        @path = path.freeze
        @handler = handler
        @middleware = middleware.freeze
        @constraints = constraints.freeze
      end

      def match?(request_method, request_path)
        return false unless request_method.upcase == @method

        pattern = @path.gsub(/:(\w+)/) { '([^/]+)' }
        regex = Regexp.new("\\A#{pattern}\\z")
        regex.match?(request_path)
      end

      def extract_params(request_path)
        param_names = @path.scan(/:(\w+)/).flatten
        pattern = @path.gsub(/:(\w+)/) { '([^/]+)' }
        regex = Regexp.new("\\A#{pattern}\\z")
        match = regex.match(request_path)

        return {} unless match

        param_names.each_with_index.each_with_object({}) do |(name, i), params|
          params[name.to_sym] = match[i + 1]
        end
      end

      def to_s
        "#{@method} #{@path}"
      end
    end

    class Router
      attr_reader :routes, :before_filters, :after_filters

      def initialize
        @routes = []
        @before_filters = []
        @after_filters = []
        @namespace_stack = []
        @total_routes_defined = 0
        @total_matches = 0
      end

      # Sinatra-style route definitions
      def get(path, handler = nil, **opts, &block)
        add_route(:get, path, handler || block, **opts)
      end

      def post(path, handler = nil, **opts, &block)
        add_route(:post, path, handler || block, **opts)
      end

      def put(path, handler = nil, **opts, &block)
        add_route(:put, path, handler || block, **opts)
      end

      def delete(path, handler = nil, **opts, &block)
        add_route(:delete, path, handler || block, **opts)
      end

      def patch(path, handler = nil, **opts, &block)
        add_route(:patch, path, handler || block, **opts)
      end

      # Rails-style namespace
      def namespace(prefix, &block)
        @namespace_stack.push(prefix.to_s)
        instance_eval(&block)
        @namespace_stack.pop
      end

      # Rails-style resources
      def resources(name, only: [:index, :show, :create, :update, :destroy])
        prefix = full_path("/#{name}")

        get("#{prefix}", ->(_) { "#{name}#index" }) if only.include?(:index)
        get("#{prefix}/:id", ->(_) { "#{name}#show" }) if only.include?(:show)
        post("#{prefix}", ->(_) { "#{name}#create" }) if only.include?(:create)
        put("#{prefix}/:id", ->(_) { "#{name}#update" }) if only.include?(:update)
        delete("#{prefix}/:id", ->(_) { "#{name}#destroy" }) if only.include?(:destroy)
      end

      # Middleware registration
      def before(&block)
        @before_filters << block
      end

      def after(&block)
        @after_filters << block
      end

      # Route matching
      def match(method, path)
        @total_matches += 1
        @routes.find { |route| route.match?(method, path) }
      end

      def dispatch(method, path, env = {})
        route = match(method, path)
        return { status: 404, body: 'Not Found' } unless route

        params = route.extract_params(path)
        request = { method: method, path: path, params: params }.merge(env)

        # Execute before filters
        @before_filters.each { |f| f.call(request) }

        # Execute handler
        result = route.handler.call(request)

        # Execute after filters
        @after_filters.each { |f| f.call(request, result) }

        { status: 200, body: result }
      end

      def diagnostics
        {
          engine: 'OmniDSLEngine::Router',
          total_routes: @routes.size,
          total_matches: @total_matches,
          routes: @routes.map(&:to_s)
        }
      end

      private

      def full_path(path)
        prefix = @namespace_stack.map { |ns| "/#{ns}" }.join
        "#{prefix}#{path}"
      end

      def add_route(method, path, handler, **opts)
        full = full_path(path)
        route = RouteDefinition.new(method, full, handler, **opts)
        @routes << route
        @total_routes_defined += 1
        route
      end
    end

    # ================================================================
    # PART 2: Configuration DSL (Builder Pattern)
    # ================================================================

    class Configuration
      attr_reader :settings

      def initialize
        @settings = {}
        @validators = {}
      end

      def self.define(&block)
        config = new
        config.instance_eval(&block)
        config.freeze_settings!
        config
      end

      def setting(name, default: nil, type: nil, required: false, &validator)
        @settings[name] = {
          value: default,
          type: type,
          required: required,
          frozen: false
        }
        @validators[name] = validator if block_given?

        # Dynamically define getter and setter
        define_singleton_method(name) { @settings[name][:value] }
        define_singleton_method(:"#{name}=") do |val|
          raise "Setting #{name} is frozen" if @settings[name][:frozen]

          if type && !val.is_a?(type)
            raise TypeError, "#{name} must be #{type}, got #{val.class}"
          end

          if @validators[name]
            unless @validators[name].call(val)
              raise ArgumentError, "Validation failed for #{name}: #{val}"
            end
          end

          @settings[name][:value] = val
        end
      end

      def group(name, &block)
        sub = Configuration.new
        sub.instance_eval(&block)
        @settings[name] = { value: sub, type: Configuration, required: false, frozen: false }

        define_singleton_method(name) { @settings[name][:value] }
      end

      def freeze_settings!
        @settings.each do |name, meta|
          if meta[:required] && meta[:value].nil?
            raise "Required setting '#{name}' is not set"
          end
        end
      end

      def to_h
        @settings.transform_values do |meta|
          val = meta[:value]
          val.is_a?(Configuration) ? val.to_h : val
        end
      end
    end

    # ================================================================
    # PART 3: Validation DSL (RSpec-inspired)
    # ================================================================

    class Validator
      attr_reader :rules, :errors

      def initialize(name)
        @name = name
        @rules = []
        @errors = []
      end

      def self.define(name, &block)
        v = new(name)
        v.instance_eval(&block)
        v
      end

      def validates(field, **opts)
        @rules << { field: field, options: opts }
      end

      def validate(data)
        @errors = []

        @rules.each do |rule|
          field = rule[:field]
          opts = rule[:options]
          value = data[field]

          if opts[:presence] && (value.nil? || value.to_s.empty?)
            @errors << "#{field} is required"
          end

          if opts[:type] && value && !value.is_a?(opts[:type])
            @errors << "#{field} must be #{opts[:type]}"
          end

          if opts[:min_length] && value.is_a?(String) && value.length < opts[:min_length]
            @errors << "#{field} must be at least #{opts[:min_length]} characters"
          end

          if opts[:max_length] && value.is_a?(String) && value.length > opts[:max_length]
            @errors << "#{field} must be at most #{opts[:max_length]} characters"
          end

          if opts[:in] && value && !opts[:in].include?(value)
            @errors << "#{field} must be one of: #{opts[:in].join(', ')}"
          end

          if opts[:format] && value.is_a?(String) && !value.match?(opts[:format])
            @errors << "#{field} has invalid format"
          end

          if opts[:custom] && opts[:custom].is_a?(Proc)
            unless opts[:custom].call(value)
              @errors << "#{field} failed custom validation"
            end
          end
        end

        @errors.empty?
      end

      def valid?
        @errors.empty?
      end
    end

    # ================================================================
    # Engine Diagnostics
    # ================================================================

    def self.diagnostics
      {
        engine: 'OmniDSLEngine',
        layer: 'Ruby Business',
        components: %w[Router Configuration Validator],
        learned_logic: [
          'instance-eval-context-shift',
          'method-missing-fluent-api',
          'define-method-runtime-methods',
          'block-as-configuration-closure',
          'namespace-stack-prefix',
          'sinatra-style-route-dsl',
          'builder-pattern-settings',
          'rspec-inspired-validation'
        ]
      }
    end
  end
end
