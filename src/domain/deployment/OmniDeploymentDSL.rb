# OmniDeploymentDSL.rb — Deployment DSL for OMNI Models
# Inspired by: Capistrano/Terraform patterns for OMNI
# Layer: Domain / Ruby
#
# Declarative deployment DSL for defining model serving
# infrastructure, rollout strategies, and monitoring.

module Omni
  module Deployment
    class DeploymentSpec
      attr_reader :name, :model_id, :version, :environment,
                  :replicas, :resources, :health_check,
                  :rollout_strategy, :scaling, :monitoring

      def initialize(name)
        @name = name
        @model_id = nil
        @version = nil
        @environment = :staging
        @replicas = 1
        @resources = ResourceSpec.new
        @health_check = HealthCheckSpec.new
        @rollout_strategy = RolloutSpec.new
        @scaling = ScalingSpec.new
        @monitoring = MonitoringSpec.new
        @hooks = { before_deploy: [], after_deploy: [],
                   on_failure: [], on_rollback: [] }
      end

      def model(id, version: "latest")
        @model_id = id
        @version = version
        self
      end

      def env(environment)
        @environment = environment.to_sym
        self
      end

      def replicas(count)
        @replicas = count
        self
      end

      def configure_resources(&block)
        block.call(@resources) if block_given?
        self
      end

      def configure_health(&block)
        block.call(@health_check) if block_given?
        self
      end

      def configure_rollout(&block)
        block.call(@rollout_strategy) if block_given?
        self
      end

      def configure_scaling(&block)
        block.call(@scaling) if block_given?
        self
      end

      def configure_monitoring(&block)
        block.call(@monitoring) if block_given?
        self
      end

      def before_deploy(&block)
        @hooks[:before_deploy] << block
        self
      end

      def after_deploy(&block)
        @hooks[:after_deploy] << block
        self
      end

      def on_failure(&block)
        @hooks[:on_failure] << block
        self
      end

      def execute_hooks(phase)
        @hooks[phase].each { |hook| hook.call(self) }
      end

      def validate!
        errors = []
        errors << "model_id required" unless @model_id
        errors << "version required" unless @version
        errors << "replicas must be positive" unless @replicas.positive?
        errors << "invalid environment" unless [:dev, :staging, :production, :edge].include?(@environment)
        @resources.validate!(errors)
        @health_check.validate!(errors)
        raise ValidationError, errors.join("; ") unless errors.empty?
        true
      end

      def to_manifest
        {
          apiVersion: "omni/v1",
          kind: "ModelDeployment",
          metadata: { name: @name, environment: @environment },
          spec: {
            model: { id: @model_id, version: @version },
            replicas: @replicas,
            resources: @resources.to_hash,
            healthCheck: @health_check.to_hash,
            rollout: @rollout_strategy.to_hash,
            scaling: @scaling.to_hash,
            monitoring: @monitoring.to_hash,
          }
        }
      end
    end

    class ResourceSpec
      attr_accessor :gpu_type, :gpu_count, :memory_gb, :cpu_cores,
                    :disk_gb, :max_batch_size, :max_sequence_length

      def initialize
        @gpu_type = "A100"
        @gpu_count = 1
        @memory_gb = 16
        @cpu_cores = 4
        @disk_gb = 50
        @max_batch_size = 64
        @max_sequence_length = 2048
      end

      def validate!(errors)
        errors << "memory_gb must be positive" unless @memory_gb.positive?
        errors << "cpu_cores must be positive" unless @cpu_cores.positive?
      end

      def to_hash
        { gpu: { type: @gpu_type, count: @gpu_count },
          memory: "#{@memory_gb}Gi", cpu: @cpu_cores,
          disk: "#{@disk_gb}Gi",
          limits: { batch_size: @max_batch_size,
                    sequence_length: @max_sequence_length } }
      end
    end

    class HealthCheckSpec
      attr_accessor :path, :interval_seconds, :timeout_seconds,
                    :failure_threshold, :success_threshold

      def initialize
        @path = "/health"
        @interval_seconds = 10
        @timeout_seconds = 5
        @failure_threshold = 3
        @success_threshold = 1
      end

      def validate!(errors)
        errors << "health check interval must be > 0" unless @interval_seconds.positive?
      end

      def to_hash
        { httpGet: { path: @path },
          intervalSeconds: @interval_seconds,
          timeoutSeconds: @timeout_seconds,
          failureThreshold: @failure_threshold,
          successThreshold: @success_threshold }
      end
    end

    class RolloutSpec
      attr_accessor :strategy, :max_surge, :max_unavailable,
                    :canary_percent, :canary_duration_minutes

      def initialize
        @strategy = :rolling_update
        @max_surge = 1
        @max_unavailable = 0
        @canary_percent = 5
        @canary_duration_minutes = 30
      end

      def to_hash
        { strategy: @strategy,
          maxSurge: @max_surge,
          maxUnavailable: @max_unavailable,
          canary: { percent: @canary_percent,
                    durationMinutes: @canary_duration_minutes } }
      end
    end

    class ScalingSpec
      attr_accessor :enabled, :min_replicas, :max_replicas,
                    :target_cpu_utilization, :target_gpu_utilization,
                    :scale_up_cooldown, :scale_down_cooldown

      def initialize
        @enabled = true
        @min_replicas = 1
        @max_replicas = 10
        @target_cpu_utilization = 70
        @target_gpu_utilization = 80
        @scale_up_cooldown = 60
        @scale_down_cooldown = 300
      end

      def to_hash
        { enabled: @enabled,
          minReplicas: @min_replicas, maxReplicas: @max_replicas,
          metrics: [
            { type: "cpu", targetUtilization: @target_cpu_utilization },
            { type: "gpu", targetUtilization: @target_gpu_utilization },
          ],
          cooldown: { scaleUp: @scale_up_cooldown,
                      scaleDown: @scale_down_cooldown } }
      end
    end

    class MonitoringSpec
      attr_accessor :metrics_enabled, :tracing_enabled,
                    :log_level, :alert_rules

      def initialize
        @metrics_enabled = true
        @tracing_enabled = true
        @log_level = :info
        @alert_rules = []
      end

      def add_alert(name, condition, severity: :warning)
        @alert_rules << { name: name, condition: condition,
                          severity: severity }
        self
      end

      def to_hash
        { metrics: @metrics_enabled, tracing: @tracing_enabled,
          logLevel: @log_level, alerts: @alert_rules }
      end
    end

    class ValidationError < StandardError; end

    # === DSL Entry Point ===

    def self.define(name, &block)
      spec = DeploymentSpec.new(name)
      block.call(spec)
      spec.validate!
      spec
    end
  end
end

# === Usage Example ===
# deployment = Omni::Deployment.define("omni-transformer-v2") do |d|
#   d.model("omni-transformer", version: "2.1.0")
#   d.env(:production)
#   d.replicas(3)
#
#   d.configure_resources do |r|
#     r.gpu_type = "A100"
#     r.gpu_count = 2
#     r.memory_gb = 32
#   end
#
#   d.configure_rollout do |r|
#     r.strategy = :canary
#     r.canary_percent = 10
#   end
#
#   d.configure_monitoring do |m|
#     m.add_alert("high_latency", "p99_latency > 500ms", severity: :critical)
#     m.add_alert("error_rate", "error_rate > 0.01", severity: :warning)
#   end
# end
