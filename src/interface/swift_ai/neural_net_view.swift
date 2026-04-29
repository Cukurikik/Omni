import SwiftUI

struct NeuralNetVisualizer: View {
    var layers: [Int] // e.g. [784, 128, 10]
    
    var body: some View {
        HStack(spacing: 50) {
            ForEach(0..<layers.count, id: \.self) { layerIdx in
                VStack(spacing: 5) {
                    Text("L\(layerIdx)")
                        .font(.caption)
                        .foregroundColor(.gray)
                    
                    // Draw up to 10 nodes per layer to avoid UI clutter
                    let displayNodes = min(layers[layerIdx], 10)
                    ForEach(0..<displayNodes, id: \.self) { _ in
                        Circle()
                            .fill(Color.blue)
                            .frame(width: 20, height: 20)
                    }
                    if layers[layerIdx] > 10 {
                        Text("...")
                    }
                }
            }
        }
        .padding()
        .background(Color.black.opacity(0.8))
        .cornerRadius(15)
    }
}
