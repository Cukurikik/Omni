// OMNI Framework - iOS Settings View (SwiftUI)
// Allows users to configure their API keys and model preferences.

import SwiftUI

struct OmniSettingsView: View {
    @AppStorage("omniApiKey") private var apiKey: String = ""
    @AppStorage("selectedModel") private var selectedModel: String = "omni-gpt-neo"
    @AppStorage("useLocalCompute") private var useLocalCompute: Bool = false
    
    let models = ["omni-gpt-neo", "omni-llama-2", "omni-sdxl"]

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Authentication")) {
                    SecureField("OMNI API Key", text: $apiKey)
                }
                
                Section(header: Text("Model Configuration")) {
                    Picker("Default Model", selection: $selectedModel) {
                        ForEach(models, id: \.self) {
                            Text($0)
                        }
                    }
                    
                    Toggle("Use On-Device Compute (NPU)", isOn: $useLocalCompute)
                        .tint(.purple)
                }
                
                Section(header: Text("About")) {
                    HStack {
                        Text("Framework Version")
                        Spacer()
                        Text("v3.0.0-OMNI-NEXUS")
                            .foregroundColor(.gray)
                    }
                }
            }
            .navigationTitle("OMNI Settings")
        }
    }
}

struct OmniSettingsView_Previews: PreviewProvider {
    static var previews: some View {
        OmniSettingsView()
    }
}
