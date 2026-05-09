# OMNI MOTHER: Ruby DSL for Expert Configuration

module OmniMoE
  class ExpertDSL
    attr_reader :experts

    def initialize
      @experts = []
    end

    def expert(name, &block)
      exp = ExpertConfig.new(name)
      exp.instance_eval(&block)
      @experts << exp
    end
  end

  class ExpertConfig
    attr_reader :name, :capacity, :model_type

    def initialize(name)
      @name = name
      @capacity = 4096
      @model_type = "mlp"
    end

    def set_capacity(val)
      @capacity = val
    end

    def set_type(type)
      @model_type = type
    end
  end
end
