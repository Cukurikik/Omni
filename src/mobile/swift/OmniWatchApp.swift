// OMNI Mobile — watchOS App App
import SwiftUI

@main
struct OmniWatchApp: App {
    var body: some Scene {
        WindowGroup {
            WatchContentView()
        }
    }
}

struct WatchContentView: View {
    @State private var status: String = "Online"
    @State private var tps: Int = 14500
    
    var body: some View {
        VStack {
            Text("OMNI Core")
                .font(.headline)
                .foregroundColor(.green)
            
            Divider()
            
            HStack {
                Text("Status:")
                Spacer()
                Text(status)
                    .foregroundColor(status == "Online" ? .green : .red)
            }
            .padding(.top, 5)
            
            HStack {
                Text("Global TPS:")
                Spacer()
                Text("\(tps)")
                    .font(.system(.body, design: .monospaced))
            }
            .padding(.top, 2)
            
            Spacer()
            
            Button(action: {
                status = "Syncing..."
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    status = "Online"
                    tps = Int.random(in: 14000...16000)
                }
            }) {
                Text("Refresh")
            }
            .tint(.blue)
        }
        .padding()
    }
}
