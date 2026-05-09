# @omni-layer Business | @omni-source microsoft/DeepSpeed | @omni-lang Ruby
# @omni-description MoE cost calculator: estimates compute cost for expert routing
# with load imbalance penalty and capacity overhead tracking.
module Omni
  module MoE
    class CostCalculator
      def initialize(n_experts:, tokens_per_batch:, expert_flops:)
        @n_experts = n_experts
        @tokens_per_batch = tokens_per_batch
        @expert_flops = expert_flops
      end

      def estimate_cost(load_distribution:, top_k: 2, capacity_factor: 1.25)
        return { error: "Invalid load" } unless load_distribution&.length == @n_experts
        ideal = @tokens_per_batch * top_k.to_f / @n_experts
        capacity = (ideal * capacity_factor).ceil
        imbalance = load_distribution.sum { |l| (l - ideal)**2 } / @n_experts
        overflow = load_distribution.count { |l| l > capacity }
        total_flops = load_distribution.sum { |l| [l, capacity].min * @expert_flops }
        wasted = load_distribution.sum { |l| [capacity - l, 0].max * @expert_flops }
        {
          data: {
            total_flops: total_flops,
            wasted_flops: wasted,
            utilization: 1.0 - wasted.to_f / [total_flops + wasted, 1].max,
            imbalance_score: imbalance,
            overflow_experts: overflow,
            capacity_per_expert: capacity,
            cost_per_token: total_flops.to_f / [@tokens_per_batch, 1].max
          }
        }
      rescue StandardError => e
        { error: e.message }
      end
    end
  end
end
