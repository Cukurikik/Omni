# Omni AI Blueprints Pipeline Service (Ruby)
# Ref: HPInc/AI-Blueprints — MIT
module Omni
  module AIBlueprints
    Pipeline = Struct.new(:id, :steps, :status, keyword_init: true)

    def self.create_pipeline(steps)
      Pipeline.new(id: "bp-#{steps.length}", steps: steps, status: 'ready')
    end

    def self.validate_step(step)
      required = %w[name type]
      missing = required - step.keys.map(&:to_s)
      { valid: missing.empty?, missing: missing }
    end

    def self.compute_metrics(y_true, y_pred)
      tp = y_true.zip(y_pred).count { |t, p| t == 1 && p == 1 }
      fp = y_true.zip(y_pred).count { |t, p| t == 0 && p == 1 }
      fn_count = y_true.zip(y_pred).count { |t, p| t == 1 && p == 0 }
      p = tp.to_f / [tp + fp, 1].max
      r = tp.to_f / [tp + fn_count, 1].max
      f1 = (p + r) > 0 ? 2 * p * r / (p + r) : 0
      { precision: p.round(4), recall: r.round(4), f1: f1.round(4) }
    end
  end
end
