# OMNI MOTHER: Ruby MoE Cluster Orchestrator
# High-level domain logic for managing the MoE lifecycle

class OmniMoEOrchestrator
  def initialize
    @experts = []
  end

  def register_expert(id, type)
    @experts << { id: id, type: type, status: 'active' }
    puts "[OMNI] Expert #{id} registered."
  end

  def prune_dead_experts(active_ids)
    @experts.reject! do |e|
      unless active_ids.include?(e[:id])
        puts "[OMNI] Pruning dead expert: #{e[:id]}"
        true
      else
        false
      end
    end
  end
end
