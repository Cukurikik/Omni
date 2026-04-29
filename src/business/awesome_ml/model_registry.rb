module Omni
  class MLCodeRegistry
    @models = {}

    def self.register(model_id, ast_type, accuracy)
      @models[model_id] = { ast_type: ast_type, accuracy: accuracy, created_at: Time.now }
    end

    def self.get_best_model
      @models.max_by { |_, data| data[:accuracy] }
    end
  end
end
