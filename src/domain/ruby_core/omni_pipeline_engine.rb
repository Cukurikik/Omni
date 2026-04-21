# ===========================================================================
# OMNI PIPELINE ENGINE (SEMESTER 3 — BATCH 38.5)
# ===========================================================================
# Absorbed From  : dry-transaction + interactor + ActiveJob pipeline
# Logic Inherited: Ruby / Business Layer (Railway-Oriented Data Pipeline)
# ===========================================================================
#
# By studying dry-transaction, Mother learned railway-oriented design:
#   1. Each step returns Success or Failure (Result monad)
#   2. Pipeline short-circuits on first Failure
#   3. Steps are composable and reorderable
#   4. Side effects (logging, metrics) are isolated as middleware
#   5. Rollback support for transactional pipelines

# frozen_string_literal: true

module Omni
  module Pipeline
    # ================================================================
    # Result Type (Monadic Error Handling)
    # ================================================================

    class Result
      attr_reader :value, :error, :metadata

      def initialize(success:, value: nil, error: nil, metadata: {})
        @success = success
        @value = value
        @error = error
        @metadata = metadata
      end

      def success?
        @success
      end

      def failure?
        !@success
      end

      # Monadic bind: chain on success only
      def bind
        return self if failure?
        yield(value)
      end

      # Map: transform value on success
      def map
        return self if failure?
        Result.success(yield(value), metadata: metadata)
      end

      # Or: handle failure path
      def or_else
        return self if success?
        yield(error)
      end

      def self.success(value, metadata: {})
        new(success: true, value: value, metadata: metadata)
      end

      def self.failure(error, metadata: {})
        new(success: false, error: error, metadata: metadata)
      end

      def to_s
        if success?
          "Success(#{value})"
        else
          "Failure(#{error})"
        end
      end

      def inspect
        to_s
      end
    end

    # ================================================================
    # Step Definition
    # ================================================================

    class Step
      attr_reader :name, :callable, :rollback_fn

      def initialize(name, callable = nil, rollback: nil, &block)
        @name = name
        @callable = callable || block
        @rollback_fn = rollback
      end

      def call(input)
        result = @callable.call(input)

        case result
        when Result
          result
        when nil
          Result.failure("Step '#{@name}' returned nil")
        else
          Result.success(result)
        end
      rescue StandardError => e
        Result.failure("Step '#{@name}' raised: #{e.message}")
      end

      def rollback(input)
        @rollback_fn&.call(input)
      end
    end

    # ================================================================
    # Middleware
    # ================================================================

    class Middleware
      def before(step_name, input); end
      def after(step_name, result, duration); end
    end

    class LoggingMiddleware < Middleware
      attr_reader :logs

      def initialize
        @logs = []
      end

      def before(step_name, _input)
        @logs << { step: step_name, event: :start, at: Time.now }
      end

      def after(step_name, result, duration)
        @logs << {
          step: step_name,
          event: :complete,
          success: result.success?,
          duration_ms: (duration * 1000).round(2),
          at: Time.now
        }
      end
    end

    class MetricsMiddleware < Middleware
      attr_reader :metrics

      def initialize
        @metrics = {
          total_steps: 0,
          successful_steps: 0,
          failed_steps: 0,
          total_duration_ms: 0.0
        }
      end

      def after(_step_name, result, duration)
        @metrics[:total_steps] += 1
        @metrics[:total_duration_ms] += (duration * 1000)

        if result.success?
          @metrics[:successful_steps] += 1
        else
          @metrics[:failed_steps] += 1
        end
      end
    end

    # ================================================================
    # Pipeline Engine
    # ================================================================

    class OmniPipelineEngine
      attr_reader :name, :steps, :middleware_stack

      def initialize(name)
        @name = name
        @steps = []
        @middleware_stack = []
        @total_executions = 0
        @total_successes = 0
        @total_failures = 0
        @total_rollbacks = 0
      end

      # DSL: Add a step
      def step(name, callable = nil, rollback: nil, &block)
        @steps << Step.new(name, callable, rollback: rollback, &block)
        self
      end

      # DSL: Add middleware
      def use(middleware)
        @middleware_stack << middleware
        self
      end

      # Execute the pipeline
      def call(input)
        @total_executions += 1
        executed_steps = []
        current = Result.success(input)

        @steps.each do |s|
          break if current.failure?

          # Before middleware
          @middleware_stack.each { |m| m.before(s.name, current.value) }

          start_time = Time.now
          current = s.call(current.value)
          duration = Time.now - start_time

          # After middleware
          @middleware_stack.each { |m| m.after(s.name, current, duration) }

          executed_steps << s if current.success?
        end

        if current.failure?
          @total_failures += 1

          # Rollback executed steps in reverse order
          executed_steps.reverse_each do |s|
            s.rollback(input)
            @total_rollbacks += 1
          end
        else
          @total_successes += 1
        end

        current
      end

      # Compose two pipelines
      def >>(other)
        composed = OmniPipelineEngine.new("#{@name}>>#{other.name}")
        @steps.each { |s| composed.steps << s }
        other.steps.each { |s| composed.steps << s }
        @middleware_stack.each { |m| composed.use(m) }
        composed
      end

      # Class method: build with DSL block
      def self.define(name, &block)
        pipeline = new(name)
        pipeline.instance_eval(&block)
        pipeline
      end

      def diagnostics
        {
          engine: 'OmniPipelineEngine',
          layer: 'Ruby Business',
          pipeline_name: @name,
          total_steps: @steps.size,
          step_names: @steps.map(&:name),
          middleware_count: @middleware_stack.size,
          total_executions: @total_executions,
          total_successes: @total_successes,
          total_failures: @total_failures,
          total_rollbacks: @total_rollbacks,
          learned_logic: [
            'railway-oriented-programming',
            'result-monad-bind-chain',
            'short-circuit-on-failure',
            'rollback-reverse-order',
            'middleware-before-after',
            'pipeline-composition-then',
            'dsl-instance-eval-builder',
            'dry-transaction-steps'
          ]
        }
      end
    end
  end
end
