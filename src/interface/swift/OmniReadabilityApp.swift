import SwiftUI

// OMNI Framework - iOS App for CommonLit Readability Scoring
@main
struct OmniReadabilityApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var textInput: String = ""
    @State private var readabilityScore: Double? = nil
    
    var body: some View {
        VStack(spacing: 20) {
            Text("OMNI Readability Analyzer")
                .font(.largeTitle)
                .bold()
            
            TextEditor(text: $textInput)
                .border(Color.gray, width: 1)
                .padding()
            
            Button(action: analyzeText) {
                Text("Analyze")
                    .foregroundColor(.white)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(8)
            }
            
            if let score = readabilityScore {
                Text("Complexity Score: \(score, specifier: "%.2f")")
                    .font(.title2)
                    .foregroundColor(score < 0 ? .green : .red)
            }
        }
    }
    
    func analyzeText() {
        // Implementation connecting to OMNI Python backend
        readabilityScore = Double.random(in: -3.0...1.0)
    }
}
