# frozen_string_literal: true

# OMNI COGNITIVE DB ENGINE
# Graph DSL constraints ensuring immutable relationships boundaries.

module Omni
  module CognitiveDB
    class GraphConsistencyEngine
      attr_reader :max_depth, :max_node_degree

      def initialize(max_depth:, max_node_degree:)
        @max_depth = max_depth
        @max_node_degree = max_node_degree
      end

      def evaluate_query_safety(node_depth, fan_out_degree)
        if node_depth < 0 || fan_out_degree < 0
          return { is_ok: false, error: "NEGATIVE_METRIC_INVALID", weight: 0.0 }
        end

        if node_depth > @max_depth
          return { is_ok: false, error: "GRAPH_DEPTH_EXCEEDED", weight: 0.0 }
        end

        if fan_out_degree > @max_node_degree
          return { is_ok: false, error: "FAN_OUT_DEGREE_EXCEEDED", weight: 0.0 }
        end

        # Computes traversal weight limit constraints
        traversal_weight = (node_depth * 1.5) + (fan_out_degree * 0.8)

        { is_ok: true, error: "", weight: traversal_weight }
      end
    end
  end
end
