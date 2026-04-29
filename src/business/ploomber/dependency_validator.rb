module Omni
  module Ploomber
    # OMNI Ploomber - Dependency Validator
    # Ruby Domain Logic for detecting circular dependencies in pipelines

    class DependencyValidator
      # input is a hash of node -> [array of dependencies]
      # { "task_b" => ["task_a"], "task_c" => ["task_b"] }
      
      def initialize(graph)
        @graph = graph
      end

      # Returns [Boolean (is_valid), String/Nil (error message)]
      def validate
        visited = {}
        recursion_stack = {}

        @graph.keys.each do |node|
          unless visited[node]
            has_cycle, cycle_path = detect_cycle_dfs(node, visited, recursion_stack, [])
            if has_cycle
              return [false, "Circular dependency detected: #{cycle_path.join(' -> ')}"]
            end
          end
        end

        [true, nil]
      end

      private

      def detect_cycle_dfs(node, visited, recursion_stack, path)
        visited[node] = true
        recursion_stack[node] = true
        path.push(node)

        dependencies = @graph[node] || []
        
        dependencies.each do |dep|
          if !visited[dep]
            has_cycle, cycle_path = detect_cycle_dfs(dep, visited, recursion_stack, path.clone)
            return [true, cycle_path] if has_cycle
          elsif recursion_stack[dep]
            path.push(dep)
            return [true, path]
          end
        end

        recursion_stack[node] = false
        path.pop
        [false, []]
      end
    end
  end
end
