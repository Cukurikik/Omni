# omni_pricing_tier.rb — Pricing Tier Definitions
# Layer: Domain / Ruby
#
# Declarative definitions of resource pricing, discounting rules, and
# tenant SLAs for the AI inference billing module.

module Omni
  module Finances
    class PricingTier
      attr_reader :tier_name, :prompt_rate, :completion_rate, :monthly_base, :sla_guarantee

      def initialize(tier_name:, prompt_rate:, completion_rate:, monthly_base: 0.0, sla_guarantee: '99.9%')
        @tier_name = tier_name
        @prompt_rate = prompt_rate
        @completion_rate = completion_rate
        @monthly_base = monthly_base
        @sla_guarantee = sla_guarantee
      end

      # Factory method returning standard plans
      def self.get_plan(plan_id)
        case plan_id.to_s.downcase
        when 'developer'
          new(
            tier_name: 'Developer',
            prompt_rate: 0.0001,
            completion_rate: 0.0002,
            monthly_base: 0.0
          )
        when 'enterprise'
          new(
            tier_name: 'Enterprise',
            prompt_rate: 0.00005,
            completion_rate: 0.0001,
            monthly_base: 500.0,
            sla_guarantee: '99.99%'
          )
        else
          raise ArgumentError, "Unknown pricing plan: #{plan_id}"
        end
      end

      # Calculates the discounted cost for volume usage
      def apply_volume_discount(total_cost, tokens_used)
        return total_cost if tokens_used < 1_000_000
        
        # 10% discount for every million tokens, up to 30% max
        discount_tiers = tokens_used / 1_000_000
        discount_percent = [discount_tiers * 0.10, 0.30].min
        
        total_cost * (1.0 - discount_percent)
      end
    end
  end
end
