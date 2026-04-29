import SwiftUI

struct ChatView: View {
    @State private var messageText = ""
    @State private var messages: [String] = []

    var body: some View {
        VStack {
            ScrollView {
                ForEach(messages, id: \.self) { msg in
                    Text(msg)
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                        .frame(maxWidth: .infinity, alignment: .trailing)
                }
            }
            HStack {
                TextField("Ask NLP Model...", text: $messageText)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                Button("Send") {
                    if !messageText.isEmpty {
                        messages.append(messageText)
                        messageText = ""
                    }
                }
            }
            .padding()
        }
    }
}
