module Omni
  module MoE
    class LoadBalancer
      def self.compute_gini(expert_loads)
        return 0.0 if expert_loads.empty?
        sorted = expert_loads.sort
        n = sorted.length
        sum = sorted.sum.to_f
        return 0.0 if sum == 0.0
        
        index_sum = sorted.each_with_index.sum { |load, i| load * (i + 1) }
        (2.0 * index_sum) / (n * sum) - (n + 1.0) / n
      end
    end
  end
end
