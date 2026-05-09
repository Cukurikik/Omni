// OMNI Interface — SwiftUI macOS Menu Bar App
import SwiftUI

struct OmniMacMenu: View {
    @State private var tps: Int = 0
    @State private var gpuTemp: Double = 45.0
    
    let timer = Timer.publish(every: 2, on: .main, in: .common).autoconnect()

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("OMNI Cluster Status")
                .font(.headline)
            
            Divider()
            
            HStack {
                Text("Throughput:")
                Spacer()
                Text("\(tps) TPS").font(.system(.body, design: .monospaced))
            }
            
            HStack {
                Text("Avg GPU Temp:")
                Spacer()
                Text(String(format: "%.1f°C", gpuTemp))
                    .foregroundColor(gpuTemp > 80 ? .red : .primary)
            }
            
            Divider()
            
            Button("Launch Full Dashboard") {
                // Launch logic here
            }
            
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
        }
        .padding()
        .frame(width: 250)
        .onReceive(timer) { _ in
            // Simulate live updates
            tps = Int.random(in: 12000...15000)
            gpuTemp = Double.random(in: 65.0...82.0)
        }
    }
}
