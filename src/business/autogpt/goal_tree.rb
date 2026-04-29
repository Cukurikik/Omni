# OMNI AUTOGPT: Autonomous Agent Goal Tree
# Ruby implementation of a hierarchical goal structure that an agent dynamically expands.
# Source: Significant-Gravitas/AutoGPT

module Omni
  module AutoGPT
    class GoalError < StandardError; end

    class GoalNode
      attr_reader :id, :description, :status
      attr_accessor :children

      def initialize(description)
        @id = SecureRandom.uuid
        @description = description
        @status = :pending # :pending, :in_progress, :completed, :failed
        @children = []
      end

      def mark_completed!
        raise GoalError, "Cannot complete: pending children exist." if @children.any? { |c| c.status != :completed }
        @status = :completed
      end

      def mark_failed!
        @status = :failed
      end

      def add_subgoal(description)
        child = GoalNode.new(description)
        @children << child
        child
      end
    end

    class AgentBrain
      attr_reader :root_goal

      def initialize(main_objective)
        @root_goal = GoalNode.new(main_objective)
      end

      # Depth-First Search to find the next actionable leaf node
      def get_next_actionable_goal(node = @root_goal)
        return nil if node.status == :completed || node.status == :failed

        if node.children.empty?
          return node
        end

        node.children.each do |child|
          actionable = get_next_actionable_goal(child)
          return actionable if actionable
        end

        # If all children are completed, this node can now be marked completed
        if node.children.all? { |c| c.status == :completed }
          node.mark_completed!
          return nil
        end

        nil
      end

      # Simulates the LLM deciding to break a goal into smaller tasks
      def expand_goal(goal_id, subgoals_descriptions, current_node = @root_goal)
        if current_node.id == goal_id
          subgoals_descriptions.each do |desc|
            current_node.add_subgoal(desc)
          end
          return true
        end

        current_node.children.each do |child|
          return true if expand_goal(goal_id, subgoals_descriptions, child)
        end

        false
      end
    end
  end
end

require 'securerandom'
