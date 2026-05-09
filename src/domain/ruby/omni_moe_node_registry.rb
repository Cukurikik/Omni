# OMNI MOTHER: Expert Node Registry (Redis Backed)

module OmniMoE
  class NodeRegistry
    def initialize
      @nodes = {}
    end

    def register(node_id, metadata)
      @nodes[node_id] = metadata
    end

    def get(node_id)
      @nodes[node_id]
    end
  end
end
