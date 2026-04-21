# ===========================================================================
# OMNI RACK ENGINE (SEMESTER 3 — BATCH 38.10)
# ===========================================================================
# Absorbed From  : Rack + Sinatra + Rails middlewares + Grape
# Logic Inherited: Ruby / Domain Layer (HTTP Interface & DSL Routing)
# ===========================================================================
#
# By studying Rack and Sinatra, Mother learned Ruby HTTP patterns:
#   1. Rack: app = object responding to #call(env) → [status, headers, body]
#   2. Middleware wraps apps: initialize(app) → call(env)
#   3. Sinatra DSL: get/post/put/delete route definitions
#   4. Before/after filters for cross-cutting concerns
#   5. Template rendering via ERB, HAML, etc.

module Omni
  module Domain
    module Ruby

      # ============================================================
      # PART 1: Rack-Compatible App Interface
      # ============================================================

      # Rack-compatible request wrapper.
      class Request
        attr_reader :method, :path, :headers, :params, :body, :env

        def initialize(env = {})
          @env     = env
          @method  = (env['REQUEST_METHOD'] || 'GET').upcase
          @path    = env['PATH_INFO'] || '/'
          @headers = extract_headers(env)
          @params  = env.fetch(:params, {})
          @body    = env.fetch(:body, nil)
        end

        def get?;    method == 'GET'; end
        def post?;   method == 'POST'; end
        def put?;    method == 'PUT'; end
        def delete?; method == 'DELETE'; end

        private

        def extract_headers(env)
          env.select { |k, _| k.to_s.start_with?('HTTP_') }
             .transform_keys { |k| k.to_s.sub('HTTP_', '').downcase.tr('_', '-') }
        end
      end

      # Rack-compatible response builder.
      class Response
        attr_accessor :status, :headers, :body

        def initialize(status: 200, headers: {}, body: '')
          @status  = status
          @headers = { 'Content-Type' => 'text/html' }.merge(headers)
          @body    = body
        end

        def json(data, status: 200)
          @status = status
          @headers['Content-Type'] = 'application/json'
          @body = data.is_a?(String) ? data : data.to_json
          self
        end

        def text(data, status: 200)
          @status = status
          @headers['Content-Type'] = 'text/plain'
          @body = data.to_s
          self
        end

        def redirect(url, status: 302)
          @status = status
          @headers['Location'] = url
          self
        end

        # Rack-compatible array format.
        def to_rack
          [@status, @headers, [@body]]
        end
      end

      # ============================================================
      # PART 2: Router with DSL
      # ============================================================

      class Router
        attr_reader :routes, :before_filters, :after_filters

        Route = Struct.new(:method, :pattern, :handler, :param_names, keyword_init: true)

        def initialize
          @routes         = []
          @before_filters = []
          @after_filters  = []
          @middleware      = []
          @total_requests  = 0
          @total_matched   = 0
        end

        # DSL methods
        def get(pattern, &block)     add_route('GET', pattern, block); end
        def post(pattern, &block)    add_route('POST', pattern, block); end
        def put(pattern, &block)     add_route('PUT', pattern, block); end
        def delete(pattern, &block)  add_route('DELETE', pattern, block); end
        def patch(pattern, &block)   add_route('PATCH', pattern, block); end

        def before(&block);  @before_filters << block; end
        def after(&block);   @after_filters << block; end
        def use(middleware);  @middleware << middleware; end

        # Rack-compatible call interface.
        def call(env)
          @total_requests += 1
          request  = Request.new(env)
          response = Response.new

          # Run before filters
          @before_filters.each { |f| f.call(request, response) }

          # Match route
          matched = match_route(request)
          if matched
            @total_matched += 1
            request.params.merge!(matched[:params])
            matched[:route].handler.call(request, response)
          else
            response.status = 404
            response.body   = '{"error": "not found"}'
            response.headers['Content-Type'] = 'application/json'
          end

          # Run after filters
          @after_filters.each { |f| f.call(request, response) }

          response.to_rack
        end

        def stats
          {
            total_routes:   @routes.size,
            total_requests: @total_requests,
            total_matched:  @total_matched,
            middleware:      @middleware.size,
            before_filters: @before_filters.size,
            after_filters:  @after_filters.size
          }
        end

        private

        def add_route(method, pattern, handler)
          param_names = pattern.scan(/:(\w+)/).flatten
          @routes << Route.new(
            method:      method,
            pattern:     pattern,
            handler:     handler,
            param_names: param_names
          )
        end

        def match_route(request)
          @routes.each do |route|
            next unless route.method == request.method
            params = match_pattern(route.pattern, request.path)
            return { route: route, params: params } if params
          end
          nil
        end

        def match_pattern(pattern, path)
          pattern_parts = pattern.split('/').reject(&:empty?)
          path_parts    = path.split('/').reject(&:empty?)
          return nil unless pattern_parts.size == path_parts.size

          params = {}
          pattern_parts.each_with_index do |part, i|
            if part.start_with?(':')
              params[part[1..].to_sym] = path_parts[i]
            elsif part != path_parts[i]
              return nil
            end
          end
          params
        end
      end

      # ============================================================
      # PART 3: Built-in Middleware
      # ============================================================

      class LoggerMiddleware
        def initialize(app)
          @app = app
          @request_count = 0
        end

        def call(env)
          @request_count += 1
          start = Time.now
          status, headers, body = @app.call(env)
          duration = ((Time.now - start) * 1000).round(2)
          method = env['REQUEST_METHOD'] || 'GET'
          path   = env['PATH_INFO'] || '/'
          puts "[#{method}] #{path} -> #{status} (#{duration}ms)"
          [status, headers, body]
        end
      end

      class CorsMiddleware
        def initialize(app, origin: '*')
          @app    = app
          @origin = origin
        end

        def call(env)
          status, headers, body = @app.call(env)
          headers['Access-Control-Allow-Origin']  = @origin
          headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
          headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
          [status, headers, body]
        end
      end

      class JsonBodyParserMiddleware
        def initialize(app)
          @app = app
        end

        def call(env)
          if env[:body].is_a?(String) && !env[:body].empty?
            begin
              env[:params] = JSON.parse(env[:body], symbolize_names: true)
            rescue JSON::ParserError
              # Leave params unchanged
            end
          end
          @app.call(env)
        end
      end

      # ============================================================
      # Diagnostics
      # ============================================================

      def self.diagnostics
        {
          engine: 'OmniRackEngine',
          layer:  'Ruby Domain',
          components: %w[Request Response Router LoggerMiddleware CorsMiddleware],
          learned_logic: [
            'rack-call-env-status-headers-body',
            'sinatra-dsl-get-post-put-delete',
            'middleware-wrap-app-pattern',
            'before-after-filter-hooks',
            'parameterized-route-matching',
            'response-builder-fluent-api',
            'struct-route-definition',
            'symbol-key-params-hash'
          ]
        }
      end

    end
  end
end
