# OMNI Fashion Domain Engine — Domain Layer
# Absorbing MohitGupta0123/Fashion-Sense-AI business rules for outfit recommendations.
# Ruby convention-over-configuration for domain logic.

class OmniFashionDomainEngine
  CATEGORIES = %w[tops bottoms shoes accessories outerwear dresses].freeze

  attr_reader :rules_applied

  def initialize
    @catalog_rules = {}
    @rules_applied = 0
  end

  def register_compatibility_rule(category_a, category_b, score)
    return { ok: false, error: "FashionDomainError: Invalid categories" } unless CATEGORIES.include?(category_a) && CATEGORIES.include?(category_b)
    return { ok: false, error: "FashionDomainError: Score must be 0.0-1.0" } unless score.between?(0.0, 1.0)

    key = [category_a, category_b].sort.join(":")
    @catalog_rules[key] = score
    { ok: true }
  end

  def score_outfit(items)
    return { ok: false, error: "FashionDomainError: Need at least 2 items" } if items.nil? || items.size < 2

    @rules_applied += 1
    total_score = 0.0
    pair_count = 0

    items.combination(2).each do |a, b|
      key = [a, b].sort.join(":")
      if @catalog_rules.key?(key)
        total_score += @catalog_rules[key]
        pair_count += 1
      end
    end

    avg = pair_count > 0 ? total_score / pair_count : 0.0
    { ok: true, outfit_score: avg, pairs_evaluated: pair_count }
  end

  def diagnostics
    { engine: "OmniFashionDomainEngine", rules: @catalog_rules.size,
      applied: @rules_applied, status: "Operational" }
  end
end
