import SwiftUI
struct OmniResult<T, E: Error> { let isOk: Bool; let value: T?; let error: E? }
enum ParallaxError: Error { case nodeLimit }
struct ParallaxClusterView: View {
    @State private var nodeCount = 0
    let maxNodes = 50
    var body: some View {
        VStack {
            Text("Parallax Cluster").font(.largeTitle)
            Text("Active Nodes: \(nodeCount)").font(.headline)
            if nodeCount > maxNodes { Text("Error: Display limit").foregroundColor(.red) }
        }
    }
    func fetchNodes() -> OmniResult<Int, ParallaxError> {
        if nodeCount > maxNodes { return OmniResult(isOk: false, value: nil, error: .nodeLimit) }
        return OmniResult(isOk: true, value: nodeCount, error: nil)
    }
}
