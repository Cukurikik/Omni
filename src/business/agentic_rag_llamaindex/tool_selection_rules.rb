module Omni
  module Business
    module AgenticRagLlamaindex
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class ToolSelectionRules
        def authorize_tool_use(agent_role, requested_tool, execution_cost)
          if execution_cost < 0
            return OmniResult.new(error: StandardError.new("Execution cost cannot be negative"))
          end

          # Agentic RAG Business Logic: Tool Authorization
          # Prevents agents from calling destructive or overly expensive APIs
          
          restricted_tools = ["drop_database", "reboot_server", "send_mass_email"]
          
          if restricted_tools.include?(requested_tool) && agent_role != "admin_agent"
            return OmniResult.new(value: { 
              authorized: false, 
              reason: "Role #{agent_role} lacks permissions for #{requested_tool}" 
            })
          end

          if execution_cost > 10.0 # Assuming $10 max budget per tool call
             return OmniResult.new(value: {
               authorized: false,
               reason: "Tool cost exceeds maximum allowed budget"
             })
          end

          OmniResult.new(value: { authorized: true, reason: "Tool call permitted" })
        end
      end
    end
  end
end
