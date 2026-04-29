import Foundation
struct OmniResult<T> { let isOk: Bool; let value: T?; let error: String? }
struct CareGPTConsultView {
    let maxSymptoms: Int = 50
    let maxTextLen: Int = 5000
    func submitConsultation(symptoms: [String], description: String) -> OmniResult<[String: Any]> {
        guard !symptoms.isEmpty else { return OmniResult(isOk: false, value: nil, error: "No symptoms") }
        guard symptoms.count <= maxSymptoms else { return OmniResult(isOk: false, value: nil, error: "Symptoms exceed \(maxSymptoms)") }
        guard description.count <= maxTextLen else { return OmniResult(isOk: false, value: nil, error: "Description too long") }
        return OmniResult(isOk: true, value: ["symptoms": symptoms.count, "status": "submitted"], error: nil)
    }
}
