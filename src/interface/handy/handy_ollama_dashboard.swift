// OMNI Interface Layer: handy_ollama_dashboard.swift
// SwiftUI Dashboard for Handy Ollama models.
// Bound: Max 20 models displayed to prevent memory pressure in mobile lists.

import SwiftUI

struct OmniError: Error {
    let code: Int
    let message: String
}

struct OmniResult<T> {
    let data: T?
    let error: OmniError?
}

struct OllamaModel: Identifiable {
    let id: String
    let name: String
    let sizeGB: Double
}

class OllamaDashboardViewModel: ObservableObject {
    let maxModels = 20
    @Published var models: [OllamaModel] = []
    @Published var errorMessage: String? = nil
    
    func appendModel(model: OllamaModel) -> OmniResult<Bool> {
        if models.count >= maxModels {
            return OmniResult(data: false, error: OmniError(code: 1, message: "Exceeded 20 model display limit."))
        }
        
        models.append(model)
        return OmniResult(data: true, error: nil)
    }
}

struct HandyOllamaDashboard: View {
    @StateObject var viewModel = OllamaDashboardViewModel()
    
    var body: some View {
        NavigationView {
            List(viewModel.models) { model in
                HStack {
                    Text(model.name)
                        .font(.headline)
                    Spacer()
                    Text(String(format: "%.1f GB", model.sizeGB))
                        .foregroundColor(.gray)
                }
            }
            .navigationTitle("Handy Ollama")
            .alert(isPresented: .constant(viewModel.errorMessage != nil)) {
                Alert(title: Text("Omni Error"), message: Text(viewModel.errorMessage ?? ""), dismissButton: .default(Text("OK")))
            }
        }
    }
}
