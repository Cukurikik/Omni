# OMNI Domain — Ruby REST Controller for Model API
# Convention-over-configuration inference endpoint.

module Omni
  module Api
    class ModelsController
      VALID_STATUSES = %w[draft validated staging production archived].freeze

      def initialize(registry)
        @registry = registry
        @stats = { total_requests: 0, errors: 0, start_time: Time.now.to_i }
      end

      def index(params = {})
        @stats[:total_requests] += 1
        status = params[:status]
        limit = (params[:limit] || 20).to_i.clamp(1, 100)
        offset = (params[:offset] || 0).to_i

        models = @registry.list(status: status, limit: limit, offset: offset)
        { status: 200, body: { models: models, total: models.length, limit: limit, offset: offset } }
      rescue => e
        error_response(500, e.message)
      end

      def show(id)
        @stats[:total_requests] += 1
        model = @registry.find(id)
        return error_response(404, "Model not found: #{id}") unless model
        { status: 200, body: model }
      end

      def create(params)
        @stats[:total_requests] += 1
        validate_create_params!(params)
        model = @registry.register(
          name: params[:name],
          architecture: params[:architecture],
          description: params[:description] || ""
        )
        { status: 201, body: model }
      rescue ArgumentError => e
        error_response(400, e.message)
      rescue => e
        error_response(500, e.message)
      end

      def deploy(id, params)
        @stats[:total_requests] += 1
        model = @registry.find(id)
        return error_response(404, "Model not found") unless model

        environment = params[:environment] || "staging"
        unless %w[staging production edge].include?(environment)
          return error_response(400, "Invalid environment: #{environment}")
        end

        result = @registry.deploy(id, environment: environment, replicas: params[:replicas] || 1)
        { status: 200, body: result }
      end

      def infer(id, params)
        @stats[:total_requests] += 1
        prompt = params[:prompt]
        return error_response(400, "Prompt is required") if prompt.nil? || prompt.empty?

        start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
        result = @registry.infer(id, prompt: prompt,
                                  max_tokens: params[:max_tokens] || 256,
                                  temperature: params[:temperature] || 0.7)
        latency = ((Process.clock_gettime(Process::CLOCK_MONOTONIC) - start) * 1000).round(2)
        result[:latency_ms] = latency
        { status: 200, body: result }
      rescue => e
        @stats[:errors] += 1
        error_response(500, e.message)
      end

      def health
        uptime = Time.now.to_i - @stats[:start_time]
        { status: 200, body: { status: "healthy", uptime_seconds: uptime, **@stats } }
      end

      private

      def validate_create_params!(params)
        raise ArgumentError, "Name is required" if params[:name].nil? || params[:name].empty?
        raise ArgumentError, "Architecture is required" if params[:architecture].nil?
      end

      def error_response(code, message)
        @stats[:errors] += 1
        { status: code, body: { error: message } }
      end
    end
  end
end
