//=============================================================================
// OMNI INTERFACE LAYER — MEDICAL SCANNER VIEW (SWIFT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: iOS native UI for doctors to interact with the MRI pipeline.
//=============================================================================

import SwiftUI
import OmniBridge

/// OMNI IDIOM: Native mobile UI accessing domain layer through bridging
public struct MedicalScannerView: View {
    @State private var patientId: String = ""
    @State private var statusMessage: String = "Ready"
    @State private var isScanning: Bool = false
    
    public init() {}
    
    public var body: some View {
        VStack(spacing: 30) {
            Text("OMNI SLATER MRI")
                .font(.system(size: 34, weight: .black, design: .rounded))
                .foregroundColor(.blue)
            
            TextField("Patient ID", text: $patientId)
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(10)
                .padding(.horizontal)
            
            ZStack {
                Circle()
                    .stroke(lineWidth: 10)
                    .opacity(0.1)
                    .foregroundColor(.blue)
                
                if isScanning {
                    Circle()
                        .trim(from: 0.0, to: 0.7)
                        .stroke(style: StrokeStyle(lineWidth: 10, lineCap: .round, lineJoin: .round))
                        .foregroundColor(.blue)
                        .rotationEffect(Angle(degrees: 360))
                        .animation(Animation.linear(duration: 1.5).repeatForever(autoreverses: false))
                }
                
                Image(systemName: "cross.case.fill")
                    .font(.system(size: 50))
                    .foregroundColor(isScanning ? .blue : .gray)
            }
            .frame(width: 200, height: 200)
            
            Text(statusMessage)
                .font(.headline)
                .foregroundColor(.secondary)
            
            Button(action: startReconstruction) {
                Text("Start K-Space Reconstruction")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(patientId.isEmpty ? Color.gray : Color.blue)
                    .cornerRadius(12)
            }
            .disabled(patientId.isEmpty || isScanning)
            .padding(.horizontal)
        }
        .padding()
    }
    
    private func startReconstruction() {
        isScanning = true
        statusMessage = "Uploading raw data..."
        
        // Call Ruby Domain Orchestrator via OMNI Event Loop
        OmniBridge.shared.invokeAsync(method: "domain.medical.workflow.initiate", payload: ["patient_id": patientId, "kspace_uri": "local://buffer/tmp1"]) { result in
            DispatchQueue.main.async {
                self.isScanning = false
                switch result {
                case .success(let data):
                    self.statusMessage = "Complete. Artifact: \(data["artifact_url"] ?? "Unknown")"
                case .failure(let error):
                    self.statusMessage = "Error: \(error.localizedDescription)"
                }
            }
        }
    }
}
