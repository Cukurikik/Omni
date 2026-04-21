# ===========================================================================
# OMNI ROUTING ENGINE (SEMESTER 3 REMEDIATION — BATCH 38.1)
# ===========================================================================
# Absorbed From  : Sinatra + Rails Router + Rack middleware concepts
# Logic Inherited: Ruby / Domain Layer (Convention-Over-Configuration Router)
# Domain Layer   : Domain (Ruby Core)
# ===========================================================================
#
# By studying Sinatra and Rails ActionDispatch::Routing, Mother learned
# that Ruby's metaprogramming enables the most expressive routing DSL:
#   1. Blocks as route handlers (Proc objects)
#   2. Regexp-based path matching with named captures
#   3. Middleware pipeline via `use` declarations
#   4. Convention-over-configuration (sensible defaults)
#   5. Before/after filters for cross-cutting concerns
#
# Ruby IS the language for rapid DSL-driven business logic in OMNI.

# frozen_string_literal: true

module OmniRoutingEngine
  # HTTP method constants
  HTTP_METHODS = %i[get post put patch delete head options].freeze

  # Represents a single route definition.
  class Route
    attr_reader :method, :path, :pattern, :handler, :filters, :params_keys

    # @param method [Symbol] HTTP method (:get, :post, etc.)
    # @param path [String] URL pattern (e.g., "/users/:id")
    # @param handler [Proc] Block to execute when matched
    # @param filters [Hash] Before/after filter chains
    def initialize(method:, path:, handler:, filters: {})
      @method = method
      @path = path
      @handler = handler
      @filters = filters
      @params_keys = []
      @pattern = compile_pattern(path)
    end

    # Check if this route matches the given method + path.
    # Returns [Boolean, Hash] — match status and extracted params.
    def match?(req_method, req_path)
      return [false, {}] unless req_method == @method

      match_data = @pattern.match(req_path)
      return [false, {}] unless match_data

      params = {}
      @params_keys.each_with_index do |key, idx|
        params[key] = match_data.captures[idx]
      end

      [true, params]
    end

    private

    # Compile a path pattern like "/users/:id/posts/:post_id"
    # into a Regexp with named captures.
    def compile_pattern(path)
      segments = path.split("/").map do |segment|
        if segment.start_with?(":")
          key = segment[1..].to_sym
          @params_keys << key
          "([^/]+)"
        elsif segment == "*"
          @params_keys << :splat
          "(.*)"
        else
          Regexp.escape(segment)
        end
      end

      Regexp.new("\\A#{segments.join('/')}\\z")
    end
  end

  # Represents a middleware layer.
  class Middleware
    attr_reader :klass, :args

    def initialize(klass, *args)
      @klass = klass
      @args = args
    end
  end

  # Request object — immutable representation of an incoming HTTP request.
  class Request
    attr_reader :method, :path, :headers, :body, :params, :query

    def initialize(method:, path:, headers: {}, body: nil, params: {}, query: {})
      @method = method.to_sym.downcase
      @path = path
      @headers = headers.freeze
      @body = body
      @params = params
      @query = query
    end

    # Merge route params into the request.
    def with_params(new_params)
      Request.new(
        method: @method,
        path: @path,
        headers: @headers,
        body: @body,
        params: @params.merge(new_params),
        query: @query
      )
    end
  end

  # Response object — builder pattern for constructing HTTP responses.
  class Response
    attr_accessor :status, :headers, :body

    def initialize(status: 200, headers: {}, body: "")
      @status = status
      @headers = { "Content-Type" => "application/json" }.merge(headers)
      @body = body
    end

    def json(data)
      @headers["Content-Type"] = "application/json"
      @body = data.is_a?(String) ? data : data.to_s
      self
    end

    def text(data)
      @headers["Content-Type"] = "text/plain"
      @body = data.to_s
      self
    end

    def status_code(code)
      @status = code
      self
    end

    def to_h
      { status: @status, headers: @headers, body: @body }
    end
  end

  # ---- Core Router Engine ----

  class Router
    attr_reader :routes, :middlewares, :before_filters, :after_filters

    def initialize(prefix: "")
      @prefix = prefix
      @routes = []
      @middlewares = []
      @before_filters = []
      @after_filters = []
      @not_found_handler = nil
      @error_handler = nil

      # Metrics
      @total_requests = 0
      @total_matches = 0
      @total_404s = 0
      @total_errors = 0
    end

    # ---- DSL Methods (Convention-Over-Configuration) ----

    HTTP_METHODS.each do |method|
      define_method(method) do |path, &handler|
        full_path = "#{@prefix}#{path}"
        @routes << Route.new(method: method, path: full_path, handler: handler)
      end
    end

    # Register middleware
    def use(middleware_class, *args)
      @middlewares << Middleware.new(middleware_class, *args)
    end

    # Before filter — runs before every matched route handler
    def before(path = nil, &block)
      @before_filters << { path: path, handler: block }
    end

    # After filter — runs after every matched route handler
    def after(path = nil, &block)
      @after_filters << { path: path, handler: block }
    end

    # Custom 404 handler
    def not_found(&handler)
      @not_found_handler = handler
    end

    # Custom error handler
    def error(&handler)
      @error_handler = handler
    end

    # ---- Routing Engine (Request Dispatch) ----

    # Dispatch an incoming request to the matching route handler.
    # @param request [Request]
    # @return [Response]
    def dispatch(request)
      @total_requests += 1

      # Find matching route
      matched_route = nil
      route_params = {}

      @routes.each do |route|
        is_match, params = route.match?(request.method, request.path)
        if is_match
          matched_route = route
          route_params = params
          break
        end
      end

      unless matched_route
        @total_404s += 1
        return handle_not_found(request)
      end

      @total_matches += 1

      # Merge route params into request
      enriched_request = request.with_params(route_params)
      response = Response.new

      begin
        # Execute before filters
        run_filters(@before_filters, enriched_request, response)

        # Execute route handler
        matched_route.handler.call(enriched_request, response)

        # Execute after filters
        run_filters(@after_filters, enriched_request, response)
      rescue => e
        @total_errors += 1
        return handle_error(e, enriched_request)
      end

      response
    end

    # ---- Namespace / Group ----

    # Create a sub-router with a path prefix.
    def namespace(prefix, &block)
      sub_router = Router.new(prefix: "#{@prefix}#{prefix}")
      sub_router.instance_eval(&block)

      # Merge sub-router's routes into this router
      @routes.concat(sub_router.routes)
    end

    # ---- Query ----

    def route_count
      @routes.length
    end

    def route_table
      @routes.map do |r|
        { method: r.method.to_s.upcase, path: r.path }
      end
    end

    # ---- Diagnostics ----

    def diagnostics
      {
        engine: "OmniRoutingEngine",
        layer: "Ruby Domain",
        total_routes: @routes.length,
        route_table: route_table,
        middleware_count: @middlewares.length,
        before_filter_count: @before_filters.length,
        after_filter_count: @after_filters.length,
        total_requests: @total_requests,
        total_matches: @total_matches,
        total_404s: @total_404s,
        total_errors: @total_errors,
        match_rate: @total_requests > 0 ?
          "#{((@total_matches.to_f / @total_requests) * 100).round(1)}%" : "N/A",
        learned_logic: [
          "sinatra-dsl-method-route-blocks",
          "regexp-path-pattern-compilation",
          "named-captures-param-extraction",
          "middleware-pipeline-use-pattern",
          "before-after-filter-chains",
          "namespace-prefix-grouping",
          "define-method-metaprogramming",
          "convention-over-configuration"
        ]
      }
    end

    private

    def run_filters(filters, request, response)
      filters.each do |filter|
        if filter[:path].nil? || request.path.match?(filter[:path])
          filter[:handler].call(request, response)
        end
      end
    end

    def handle_not_found(request)
      if @not_found_handler
        response = Response.new(status: 404)
        @not_found_handler.call(request, response)
        response
      else
        Response.new(status: 404).json('{"error": "Not Found"}')
      end
    end

    def handle_error(error, request)
      if @error_handler
        response = Response.new(status: 500)
        @error_handler.call(error, request, response)
        response
      else
        Response.new(status: 500).json("{\"error\": \"#{error.message}\"}")
      end
    end
  end
end
