module Omni
  module Strands
    class AgentContract
      attr_reader :agent_id, :capabilities, :max_steps

      def initialize(agent_id, capabilities)
        @agent_id = agent_id
        @capabilities = capabilities # Array of tools allowed
        @max_steps = 15
        @status = :idle
      end

      def authorize_tool_execution(tool_name)
        unless @capabilities.include?(tool_name)
          raise SecurityError, "Agent #{@agent_id} is not authorized to execute #{tool_name}"
        end
        true
      end

      def validate_budget(current_steps)
        if current_steps >= @max_steps
          raise "Agent execution budget exceeded (#{@max_steps} steps limit)"
        end
        true
      end
    end
  end
end
