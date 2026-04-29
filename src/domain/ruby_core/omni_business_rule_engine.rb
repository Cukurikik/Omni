# Omni Business Rule Engine (Ruby)
# Strict Domain logic, returning pseudo-Monads.

module Omni
  class Result
    attr_reader :value, :error, :success

    def initialize(success:, value: nil, error: nil)
      @success = success
      @value = value
      @error = error
    end

    def self.ok(value)
      new(success: true, value: value)
    end

    def self.err(error)
      new(success: false, error: error)
    end
  end

  class BusinessRuleEngine
    def evaluate_discount(user_tier, purchase_amount)
      return Result.err("Amount must be positive") if purchase_amount <= 0

      discount = case user_tier
                 when :premium then purchase_amount * 0.2
                 when :standard then purchase_amount * 0.05
                 else 0.0
                 end

      Result.ok(discount.round(2))
    end
  end
end
