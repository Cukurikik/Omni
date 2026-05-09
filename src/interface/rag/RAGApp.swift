//=============================================================================
// OMNI INTERFACE LAYER — RAG ASSISTANT APP ENTRY (SWIFT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: iOS Native App Entry point for the RAG Document Assistant.
//=============================================================================

import SwiftUI
import OmniBridge

@main
struct OmniRAGApp: App {
    
    init() {
        // OMNI IDIOM: Initialize the cross-language FFI bridge on app boot
        OmniBridge.shared.initialize(configPath: "Omnifile.toml")
    }

    var body: some Scene {
        WindowGroup {
            RAGAssistantView()
                .preferredColorScheme(.dark)
        }
    }
}

struct RAGAssistantView: View {
    @State private var query: String = ""
    @State private var responses: [String] = []
    
    var body: some View {
        NavigationView {
            VStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(responses, id: \.self) { res in
                            Text(res)
                                .padding()
                                .background(Color.blue.opacity(0.2))
                                .cornerRadius(12)
                                .padding(.horizontal)
                        }
                    }
                }
                
                HStack {
                    TextField("Ask the documents...", text: $query)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .padding(.leading)
                    
                    Button(action: sendQuery) {
                        Image(systemName: "paperplane.fill")
                            .foregroundColor(.white)
                            .padding()
                            .background(Color.blue)
                            .clipShape(Circle())
                    }
                    .padding(.trailing)
                }
                .padding(.bottom)
            }
            .navigationTitle("OMNI RAG Nexus")
        }
    }
    
    private func sendQuery() {
        guard !query.isEmpty else { return }
        let currentQuery = query
        query = ""
        responses.append("You: \(currentQuery)")
        
        // Dispatch to Go Network Layer -> Python Embedder -> Rust Vector DB -> LLM
        OmniBridge.shared.invokeAsync(method: "network.rag.query", payload: ["text": currentQuery]) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let data):
                    self.responses.append("Omni: \(data["answer"] as? String ?? "No answer")")
                case .failure(let error):
                    self.responses.append("Error: \(error.localizedDescription)")
                }
            }
        }
    }
}
