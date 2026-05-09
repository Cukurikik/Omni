# @omni-layer Business | @omni-source lucidrains/ETSformer-pytorch | @omni-lang Ruby
# @omni-description Forecasting service registry: domain layer for time series
# model registration, evaluation tracking, and forecast serving.

module OmniForecastRegistry
  class OmniResult
    attr_reader :data, :error
    def initialize(data: nil, error: nil); @data = data; @error = error; end
    def ok?; @error.nil?; end
  end

  class ForecastModel
    attr_accessor :id, :name, :model_type, :params, :metrics, :status, :created_at
    def initialize(id:, name:, model_type:, params: {})
      @id = id; @name = name; @model_type = model_type
      @params = params; @metrics = {}; @status = :registered
      @created_at = Time.now
    end

    def to_h
      { id: @id, name: @name, model_type: @model_type,
        params: @params, metrics: @metrics, status: @status }
    end
  end

  class Registry
    def initialize
      @models = {}
      @evaluations = []
    end

    def register_model(id:, name:, model_type:, params: {})
      model = ForecastModel.new(id: id, name: name, model_type: model_type, params: params)
      @models[id] = model
      OmniResult.new(data: { registered: id, total: @models.size })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def evaluate_model(id:, metrics:)
      model = @models[id]
      return OmniResult.new(error: "Model #{id} not found") unless model
      model.metrics.merge!(metrics)
      model.status = :evaluated
      @evaluations << { model_id: id, metrics: metrics, timestamp: Time.now }
      OmniResult.new(data: { model_id: id, metrics: model.metrics })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def leaderboard(metric_key: :mse, ascending: true)
      evaluated = @models.values.select { |m| m.metrics.key?(metric_key) }
      sorted = evaluated.sort_by { |m| m.metrics[metric_key] }
      sorted.reverse! unless ascending
      OmniResult.new(data: sorted.map.with_index { |m, i|
        { rank: i + 1, id: m.id, name: m.name,
          score: m.metrics[metric_key], all_metrics: m.metrics }
      })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def deploy_model(id:)
      model = @models[id]
      return OmniResult.new(error: "Model #{id} not found") unless model
      model.status = :deployed
      OmniResult.new(data: { deployed: id, status: :deployed })
    rescue => e
      OmniResult.new(error: e.message)
    end

    def stats
      {
        total_models: @models.size,
        evaluated: @models.values.count { |m| m.status == :evaluated },
        deployed: @models.values.count { |m| m.status == :deployed },
        evaluations: @evaluations.size
      }
    end
  end
end
