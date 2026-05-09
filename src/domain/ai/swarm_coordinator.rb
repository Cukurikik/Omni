#=============================================================================
# OMNI DOMAIN LAYER — SWARM COORDINATOR (RUBY)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Ruby Domain logic to orchestrate multi-agent interactions within 
#              the Swarms framework.
#=============================================================================

require 'omni_bridge/domain'

module Omni
  module Domain
    module AI
      class SwarmCoordinator
        
        # OMNI IDIOM: Monadic Result flow
        def self.dispatch_task(task_description, required_role)
          Omni::Result.attempt do
            # 1. Fetch available agents from Go Model Registry via Omni Bridge
            registry_res = Omni::Bridge::EventLoop.call_sync("domain.models.list_active", {})
            raise "Cannot access agent registry" unless registry_res.success?

            available_agents = registry_res.data["agents"]
            
            # 2. Select appropriate agent
            selected_agent = available_agents.find do |agent| 
              agent["role"] == required_role && agent["status"] == 'IDLE'
            end

            raise "No available agents for role: #{required_role}" unless selected_agent

            # 3. Publish task to Go Event Bus
            pub_res = Omni::Bridge::EventLoop.call_sync("network.event.swarm_publish", {
              topic: "agent_#{selected_agent['id']}_inbox",
              payload: { task: task_description, priority: 1 }
            })

            raise "Failed to dispatch task to agent" unless pub_res.success?

            { status: "Dispatched", assigned_agent_id: selected_agent['id'] }
          end
        end

      end
    end
  end
end
