# @omni-layer Business | @omni-source dmlc/torchblocks | @omni-lang Ruby
# @omni-description NLP model registry: domain layer for transformer model
# lifecycle, benchmark tracking, multi-task evaluation, and deployment.

module OmniNLPRegistry
  class OmniResult
    attr_reader :data, :error
    def initialize(data: nil, error: nil); @data = data; @error = error; end
    def ok?; @error.nil?; end
  end

  class NLPModel
    attr_accessor :id, :name, :architecture, :task_type, :params_m, :status, :benchmarks, :created_at
    def initialize(id:, name:, architecture:, task_type:, params_m:)
      @id = id; @name = name; @architecture = architecture
      @task_type = task_type; @params_m = params_m
      @status = :registered; @benchmarks = {}; @created_at = Time.now
    end
  end

  class NLPModelRegistry
    def initialize
      @models = {}
      @evaluations = []
    end

    def register_model(id:, name:, architecture:, task_type:, params_m:)
      model = NLPModel.new(id: id, name: name, architecture: architecture, task_type: task_type, params_m: params_m)
      @models[id] = model
      OmniResult.new(data: { registered: id, total: @models.size })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def evaluate(id:, benchmark:, metrics:)
      model = @models[id]
      return OmniResult.new(error: "Model not found") unless model
      model.benchmarks[benchmark] = metrics
      model.status = :evaluated
      @evaluations << { model_id: id, benchmark: benchmark, metrics: metrics, timestamp: Time.now }
      OmniResult.new(data: { model_id: id, benchmark: benchmark, metrics: metrics })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def deploy(id:)
      model = @models[id]
      return OmniResult.new(error: "Model not found") unless model
      model.status = :deployed
      OmniResult.new(data: { deployed: id })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def leaderboard(benchmark:, metric_key: :f1, ascending: false)
      models_with_bench = @models.values.select { |m| m.benchmarks.key?(benchmark) }
      sorted = models_with_bench.sort_by { |m| m.benchmarks[benchmark][metric_key] || 0 }
      sorted.reverse! unless ascending
      OmniResult.new(data: sorted.map.with_index { |m, i|
        { rank: i+1, id: m.id, name: m.name, score: m.benchmarks[benchmark][metric_key],
          architecture: m.architecture, params_m: m.params_m }
      })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def stats
      { total_models: @models.size,
        evaluated: @models.values.count { |m| m.status == :evaluated },
        deployed: @models.values.count { |m| m.status == :deployed },
        total_evals: @evaluations.size }
    end
  end
end
