// Medical Imaging Viewer
import Foundation

struct OmniResult<T, E: Error> {
    let isOk: Bool
    let value: T?
    let error: E?
}

enum MedicalError: Error {
    case invalidContrast
}

class MedicalViewer {
    func adjustContrast(level: Double) -> OmniResult<Double, MedicalError> {
        if level < 0.0 || level > 1.0 {
            return OmniResult(isOk: false, value: nil, error: .invalidContrast)
        }
        return OmniResult(isOk: true, value: level * 2.0, error: nil)
    }
}
