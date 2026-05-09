// OmniChatCLI.swift — Native Swift Local Chat Client
// Inspired by: local-chat
// Layer: Interface / Swift
//
// Terminal-based chat interface written in Swift. Connects to the local
// OMNI inference gateway via HTTP streaming.

import Foundation

struct Message: Codable {
    let role: String
    let content: String
}

struct ChatRequest: Codable {
    let model: String
    let messages: [Message]
    let stream: Bool
}

class OmniChatCLI {
    let endpoint: String
    var conversationHistory: [Message] = []
    let session = URLSession(configuration: .default)

    init(endpoint: String = "http://127.0.0.1:8080/v1/chat/completions") {
        self.endpoint = endpoint
    }

    func start() {
        print("🪐 OMNI Local Terminal Chat (Type 'exit' to quit)\n")
        
        while true {
            print("You: ", terminator: "")
            guard let input = readLine(), !input.trimmingCharacters(in: .whitespaces).isEmpty else {
                continue
            }
            
            if input.lowercased() == "exit" {
                break
            }

            conversationHistory.append(Message(role: "user", content: input))
            
            let semaphore = DispatchSemaphore(value: 0)
            print("Omni: ", terminator: "")
            
            streamResponse { fullResponse in
                self.conversationHistory.append(Message(role: "assistant", content: fullResponse))
                print("\n")
                semaphore.signal()
            }
            
            semaphore.wait()
        }
    }

    private func streamResponse(completion: @escaping (String) -> Void) {
        guard let url = URL(string: endpoint) else { return }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload = ChatRequest(model: "omni-local", messages: conversationHistory, stream: true)
        request.httpBody = try? JSONEncoder().encode(payload)

        let task = session.dataTask(with: request) { data, response, error in
            if let error = error {
                print("[Error connecting to engine: \(error.localizedDescription)]")
                completion("")
                return
            }
            
            // In a real streaming scenario, we would use URLSessionDataDelegate 
            // to capture chunks as they arrive. For CLI simplicity in this example, 
            // we process the buffered response.
            guard let data = data, let text = String(data: data, encoding: .utf8) else {
                completion("")
                return
            }
            
            var fullText = ""
            let lines = text.components(separatedBy: "\n")
            for line in lines where line.hasPrefix("data: ") {
                let jsonStr = line.dropFirst(6)
                if jsonStr.trimmingCharacters(in: .whitespaces) == "[DONE]" {
                    break
                }
                
                if let jsonData = jsonStr.data(using: .utf8),
                   let dict = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any],
                   let choices = dict["choices"] as? [[String: Any]],
                   let delta = choices.first?["delta"] as? [String: Any],
                   let content = delta["content"] as? String {
                    
                    fullText += content
                    print(content, terminator: "")
                    fflush(stdout)
                }
            }
            completion(fullText)
        }
        task.resume()
    }
}

// To run in script mode:
// let cli = OmniChatCLI()
// cli.start()
