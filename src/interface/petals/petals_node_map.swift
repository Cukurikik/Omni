import SwiftUI

enum OmniResult<T> {
    case ok(T)
    case err(String)
}

struct NodeMetrics {
    var nodeId: String
    var shardCount: Int
    var active: Bool
}

class PetalsMapController: ObservableObject {
    @Published var activeNodes: [NodeMetrics] = []
    @Published var systemError: String?
    
    let MAX_NODES_RENDERED = 100
    
    func registerNode(id: String, shards: Int) -> OmniResult<Void> {
        if activeNodes.count >= MAX_NODES_RENDERED {
            return .err("OMNI_LIMIT: Max nodes reached in UI topology")
        }
        
        if shards <= 0 {
            return .err("OMNI_ERROR: Shard count must be positive")
        }
        
        activeNodes.append(NodeMetrics(nodeId: id, shardCount: shards, active: true))
        return .ok(())
    }
    
    func handleNewNode(id: String, shards: Int) {
        let res = registerNode(id: id, shards: shards)
        if case .err(let msg) = res {
            self.systemError = msg
        }
    }
}

struct PetalsNodeMapView: View {
    @StateObject var controller = PetalsMapController()
    
    var body: some View {
        VStack {
            Text("Petals Decentralized Topology")
                .font(.headline)
            
            if let err = controller.systemError {
                Text(err).foregroundColor(.red).padding()
            }
            
            List(controller.activeNodes, id: \.nodeId) { node in
                HStack {
                    Text("Node: \(node.nodeId)")
                    Spacer()
                    Text("Shards: \(node.shardCount)")
                    Circle()
                        .fill(node.active ? Color.green : Color.red)
                        .frame(width: 10, height: 10)
                }
            }
        }
    }
}
