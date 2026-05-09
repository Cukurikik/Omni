import SwiftUI

// OMNI MOTHER: Swift iOS App Entry Point

@main
struct OmniMoEiOSApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    var body: some View {
        VStack {
            Text("OMNI MOTHER")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.blue)
            Text("MoE Mobile Dashboard")
                .font(.subheadline)
                .foregroundColor(.gray)
        }
        .padding()
        .preferredColorScheme(.dark)
    }
}
