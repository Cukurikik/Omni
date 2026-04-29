module Omni
  module Graph
    class Result
      attr_reader :is_success, :value, :error
      def initialize(is_success, value, error); @is_success = is_success; @value = value; @error = error; end
      def self.success(value); new(true, value, nil); end
      def self.failure(error); new(false, nil, error); end
    end

    class TraversalDSL
      def initialize
        @steps = []
      end

      def v(id)
        @steps << { action: :match_vertex, id: id }
        self
      end

      def out_e(label = nil)
        @steps << { action: :traverse_out_edge, label: label }
        self
      end

      def in_v(label = nil)
        @steps << { action: :match_in_vertex, label: label }
        self
      end
      
      def filter(properties)
        @steps << { action: :filter, properties: properties }
        self
      end

      def compile
        begin
          # In production, this would compile to a Cypher query or raw Pregel execution plan
          query_plan = @steps.map do |step|
            case step[:action]
            when :match_vertex
              "MATCH (v:#{step[:id]})"
            when :traverse_out_edge
              "-[e:#{step[:label] || '*'}]->"
            when :match_in_vertex
              "(in_v:#{step[:label] || '*'})"
            when :filter
              props = step[:properties].map { |k, v| "#{k}: '#{v}'" }.join(', ')
              "WHERE {#{props}}"
            else
              raise "Unknown step action"
            end
          end.join(" ")
          
          Result.success({
            plan: query_plan,
            raw_steps: @steps
          })
        rescue StandardError => e
          Result.failure("Compilation failed: #{e.message}")
        end
      end
    end
  end
end
