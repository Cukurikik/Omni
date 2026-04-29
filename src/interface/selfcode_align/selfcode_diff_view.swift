import SwiftUI
// OMNI-BRIDGE: import SelfCodeAlignSIMD via C FFI

/// OMNI Monadic Enum in Swift
enum OmniResult<T> {
    case ok(T)
    case err(String)
}

struct ASTDiffState {
    var similarityScore: Double
    var isAligned: Bool
}

class SelfCodeAlignController: ObservableObject {
    @Published var diffState: ASTDiffState?
    @Published var errorMessage: String?
    
    private let THRESHOLD: Double = 0.85
    
    func processASTAlignment(score: Double) -> OmniResult<ASTDiffState> {
        if score < 0.0 || score > 1.0 {
            return .err("OMNI_ERROR: Invalid similarity score from compute layer.")
        }
        
        let state = ASTDiffState(
            similarityScore: score,
            isAligned: score >= THRESHOLD
        )
        return .ok(state)
    }
    
    func updateUI(with score: Double) {
        let result = processASTAlignment(score: score)
        switch result {
        case .ok(let state):
            self.diffState = state
            self.errorMessage = nil
        case .err(let err):
            self.errorMessage = err
            self.diffState = nil
        }
    }
}

struct SelfCodeDiffView: View {
    @StateObject var controller = SelfCodeAlignController()
    
    var body: some View {
        VStack {
            Text("SelfCodeAlign OMNI Diff")
                .font(.headline)
            
            if let err = controller.errorMessage {
                Text(err).foregroundColor(.red)
            } else if let state = controller.diffState {
                Text("Similarity: \(String(format: "%.2f", state.similarityScore))")
                Text("Aligned: \(state.isAligned ? "YES" : "NO")")
                    .foregroundColor(state.isAligned ? .green : .orange)
            } else {
                Text("Waiting for compute layer...")
            }
        }
        .padding()
    }
}
