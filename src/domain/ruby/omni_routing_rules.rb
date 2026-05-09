# OMNI MOTHER: Ruby Dynamic Routing Rules

module OmniMoE
  class RoutingRules
    def self.fallback_allowed?(expert_status)
      expert_status != 'FAILED' && expert_status != 'OFFLINE'
    end

    def self.calculate_priority(latency, load)
      # Lower score is better
      latency * 0.7 + load * 0.3
    end
  end
end
