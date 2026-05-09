// OMNI Framework - Vision MoE Client (SwiftUI)
// iOS interface for capturing images and passing them to the MoE-LLaVA backend

import SwiftUI
import PhotosUI

struct OmniVisionMoEView: View {
    @State private var selectedItem: PhotosPickerItem? = nil
    @State private var selectedImageData: Data? = nil
    @State private var promptText: String = ""
    @State private var isProcessing: Bool = false
    @State private var resultText: String = "Select an image and ask a question."

    var body: some View {
        VStack(spacing: 20) {
            Text("OMNI Vision MoE")
                .font(.largeTitle)
                .bold()
                .padding(.top)

            if let selectedImageData, let uiImage = UIImage(data: selectedImageData) {
                Image(uiImage: uiImage)
                    .resizable()
                    .scaledToFit()
                    .frame(height: 250)
                    .cornerRadius(12)
            } else {
                Rectangle()
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 250)
                    .cornerRadius(12)
                    .overlay(Text("No Image Selected").foregroundColor(.gray))
            }

            PhotosPicker(
                selection: $selectedItem,
                matching: .images,
                photoLibrary: .shared()) {
                    Text("Select Image")
                        .fontWeight(.semibold)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
                .onChange(of: selectedItem) { newItem in
                    Task {
                        if let data = try? await newItem?.loadTransferable(type: Data.self) {
                            selectedImageData = data
                        }
                    }
                }

            TextField("Ask about the image...", text: $promptText)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)

            Button(action: analyzeImage) {
                if isProcessing {
                    ProgressView().tint(.white)
                } else {
                    Text("Analyze with MoE-LLaVA")
                        .fontWeight(.semibold)
                }
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(promptText.isEmpty || selectedImageData == nil ? Color.gray : Color.green)
            .foregroundColor(.white)
            .cornerRadius(10)
            .disabled(promptText.isEmpty || selectedImageData == nil || isProcessing)

            ScrollView {
                Text(resultText)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.black.opacity(0.05))
                    .cornerRadius(8)
            }

            Spacer()
        }
        .padding()
    }

    func analyzeImage() {
        isProcessing = true
        resultText = "Transmitting to OMNI Server..."
        
        // Mocking network call to Python MoE-LLaVA backend
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            self.resultText = "OMNI MoE Output: The image shows a serene landscape. Visual patches were routed to Expert 2 (Nature) and Expert 4 (Lighting)."
            self.isProcessing = false
        }
    }
}

struct OmniVisionMoEView_Previews: PreviewProvider {
    static var previews: some View {
        OmniVisionMoEView()
    }
}
