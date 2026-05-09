# moe_config_dsl.rb — MoE Configuration DSL
# Layer: Domain / Configuration — MoE DSL (Ruby)
#
# Ruby DSL for declarative MoE model configuration.
# Convention-over-configuration approach for defining expert
# architectures, routing strategies, and deployment targets.

module Omni
  module MoE
    class ConfigError < StandardError; end

    class ExpertDefinition
      attr_reader :id, :hidden_dim, :ff_dim, :activation, :dropout,
                  :quantization, :device, :tags

      def initialize(id)
        @id = id
        @hidden_dim = 768
        @ff_dim = 3072
        @activation = :silu
        @dropout = 0.0
        @quantization = :none
        @device = :auto
        @tags = []
      end

      def dimensions(hidden:, ff:)
        @hidden_dim = hidden
        @ff_dim = ff
        self
      end

      def activate_with(fn)
        @activation = fn
        self
      end

      def dropout_rate(rate)
        @dropout = rate
        self
      end

      def quantize(method)
        @quantization = method
        self
      end

      def on_device(device_id)
        @device = device_id
        self
      end

      def tag(*labels)
        @tags.concat(labels)
        self
      end

      def to_h
        {
          id: @id, hidden_dim: @hidden_dim, ff_dim: @ff_dim,
          activation: @activation, dropout: @dropout,
          quantization: @quantization, device: @device, tags: @tags
        }
      end
    end

    class RouterDefinition
      attr_reader :strategy, :top_k, :capacity_factor, :noise_std,
                  :load_balance_weight, :z_loss_weight

      def initialize
        @strategy = :top_k
        @top_k = 2
        @capacity_factor = 1.25
        @noise_std = 0.1
        @load_balance_weight = 0.01
        @z_loss_weight = 1e-4
      end

      def use_strategy(s)
        @strategy = s
        self
      end

      def select_top(k)
        @top_k = k
        self
      end

      def capacity(factor)
        @capacity_factor = factor
        self
      end

      def noise(std)
        @noise_std = std
        self
      end

      def balance_weight(w)
        @load_balance_weight = w
        self
      end

      def to_h
        {
          strategy: @strategy, top_k: @top_k,
          capacity_factor: @capacity_factor, noise_std: @noise_std,
          load_balance_weight: @load_balance_weight,
          z_loss_weight: @z_loss_weight
        }
      end
    end

    class DeploymentTarget
      attr_reader :name, :replicas, :device_type, :memory_limit_gb,
                  :auto_scale, :health_check_interval

      def initialize(name)
        @name = name
        @replicas = 1
        @device_type = :gpu
        @memory_limit_gb = 16
        @auto_scale = false
        @health_check_interval = 10
      end

      def with_replicas(n)
        @replicas = n
        self
      end

      def on(device)
        @device_type = device
        self
      end

      def memory_limit(gb)
        @memory_limit_gb = gb
        self
      end

      def auto_scale!
        @auto_scale = true
        self
      end

      def health_check_every(seconds)
        @health_check_interval = seconds
        self
      end

      def to_h
        {
          name: @name, replicas: @replicas, device_type: @device_type,
          memory_limit_gb: @memory_limit_gb, auto_scale: @auto_scale,
          health_check_interval: @health_check_interval
        }
      end
    end

    # Main DSL class for MoE configuration
    class ModelConfig
      attr_reader :name, :version, :experts, :router, :deployment,
                  :hidden_dim, :num_layers, :num_heads, :vocab_size

      def initialize(name, &block)
        @name = name
        @version = "1.0.0"
        @hidden_dim = 768
        @num_layers = 12
        @num_heads = 12
        @vocab_size = 32_000
        @experts = []
        @router = RouterDefinition.new
        @deployment = nil
        @training = {}

        instance_eval(&block) if block_given?
        validate!
      end

      # DSL methods

      def version(v)
        @version = v
      end

      def architecture(hidden_dim:, num_layers:, num_heads:, vocab_size: 32_000)
        @hidden_dim = hidden_dim
        @num_layers = num_layers
        @num_heads = num_heads
        @vocab_size = vocab_size
      end

      def expert(id, &block)
        ed = ExpertDefinition.new(id)
        ed.dimensions(hidden: @hidden_dim, ff: @hidden_dim * 4)
        ed.instance_eval(&block) if block_given?
        @experts << ed
      end

      def experts_count(n, &block)
        n.times do |i|
          expert(i, &block)
        end
      end

      def routing(&block)
        @router.instance_eval(&block) if block_given?
      end

      def deploy(name, &block)
        @deployment = DeploymentTarget.new(name)
        @deployment.instance_eval(&block) if block_given?
      end

      def training(lr:, warmup_steps: 1000, max_steps: 100_000, batch_size: 32)
        @training = {
          learning_rate: lr,
          warmup_steps: warmup_steps,
          max_steps: max_steps,
          batch_size: batch_size
        }
      end

      def to_h
        {
          name: @name, version: @version,
          architecture: {
            hidden_dim: @hidden_dim, num_layers: @num_layers,
            num_heads: @num_heads, vocab_size: @vocab_size
          },
          experts: @experts.map(&:to_h),
          router: @router.to_h,
          deployment: @deployment&.to_h,
          training: @training
        }
      end

      def to_toml
        generate_toml(to_h)
      end

      private

      def validate!
        raise ConfigError, "Model name required" if @name.nil? || @name.empty?
        raise ConfigError, "At least 2 experts required" if @experts.size < 2
        raise ConfigError, "Hidden dim must be positive" if @hidden_dim <= 0

        if @router.top_k > @experts.size
          raise ConfigError, "top_k (#{@router.top_k}) > num_experts (#{@experts.size})"
        end
      end

      def generate_toml(hash, prefix = "")
        lines = []
        hash.each do |key, value|
          full_key = prefix.empty? ? key.to_s : "#{prefix}.#{key}"
          case value
          when Hash
            lines << "[#{full_key}]"
            lines << generate_toml(value, "")
          when Array
            if value.first.is_a?(Hash)
              value.each do |item|
                lines << "[[#{full_key}]]"
                lines << generate_toml(item, "")
              end
            else
              lines << "#{key} = #{value.inspect}"
            end
          when String, Symbol
            lines << "#{key} = \"#{value}\""
          when Numeric
            lines << "#{key} = #{value}"
          when TrueClass, FalseClass
            lines << "#{key} = #{value}"
          when NilClass
            # skip
          end
        end
        lines.join("\n")
      end
    end

    # Factory method for DSL usage
    def self.define(name, &block)
      ModelConfig.new(name, &block)
    end
  end
end

# Example usage:
# config = Omni::MoE.define("my-moe-model") do
#   version "2.0.0"
#   architecture hidden_dim: 1024, num_layers: 24, num_heads: 16
#   experts_count(16) do
#     dimensions hidden: 1024, ff: 4096
#     activate_with :silu
#     dropout_rate 0.05
#   end
#   routing do
#     use_strategy :top_k
#     select_top 2
#     capacity 1.25
#     balance_weight 0.01
#   end
#   deploy "production" do
#     with_replicas 4
#     on :gpu
#     memory_limit 80
#     auto_scale!
#   end
# end
