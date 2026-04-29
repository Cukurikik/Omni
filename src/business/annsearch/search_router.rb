module Omni
  module Business
    module ANNSearch
      
      class OmniResult
        attr_reader :data, :error
        
        def initialize(data: nil, error: nil)
          @data = data
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class SearchRouter
        def initialize(max_connections: 100)
          @max_connections = max_connections
          @cluster_map = {
            "euclidean" => "cluster-alpha",
            "cosine" => "cluster-beta",
            "dot_product" => "cluster-gamma"
          }
        end

        def route_query(vector_payload, metric_type)
          return OmniResult.new(error: "Payload cannot be empty") if vector_payload.nil? || vector_payload.empty?
          return OmniResult.new(error: "Unsupported metric type") unless @cluster_map.key?(metric_type)
          
          target_cluster = @cluster_map[metric_type]
          
          # Compute query load hash
          load_hash = vector_payload.hash.abs % @max_connections
          
          routing_instruction = {
            cluster: target_cluster,
            node_id: "node-#{load_hash}",
            priority: vector_payload.length > 512 ? "high" : "standard"
          }
          
          OmniResult.new(data: routing_instruction)
        end
      end
      
    end
  end
end
