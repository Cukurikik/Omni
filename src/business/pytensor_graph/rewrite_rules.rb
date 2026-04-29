module Omni
  module Business
    module PyTensorGraph
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

      class RewriteRules
        def validate_graph_acyclic(edges)
          return OmniResult.new(error: StandardError.new("Edges cannot be nil")) if edges.nil?

          # Deterministic cycle detection (Business Rule: Computation Graphs MUST be DAGs)
          visited = {}
          rec_stack = {}
          
          # Build adjacency list
          adj = Hash.new { |h, k| h[k] = [] }
          edges.each do |edge|
            adj[edge[:from]] << edge[:to]
          end

          has_cycle = false
          check_cycle = ->(node) do
            visited[node] = true
            rec_stack[node] = true
            
            adj[node].each do |neighbor|
              if !visited[neighbor] && check_cycle.call(neighbor)
                return true
              elsif rec_stack[neighbor]
                return true
              end
            end
            
            rec_stack[node] = false
            false
          end

          adj.keys.each do |node|
            if !visited[node]
              if check_cycle.call(node)
                has_cycle = true
                break
              end
            end
          end

          if has_cycle
            return OmniResult.new(error: StandardError.new("Cycle detected in computation graph. Must be a DAG."))
          end

          OmniResult.new(value: true)
        end
      end
    end
  end
end
