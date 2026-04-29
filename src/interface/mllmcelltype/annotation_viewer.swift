import Foundation

struct OmniResult<T> {
    let value: T?
    let error: String?
    var isOk: Bool { return error == nil }
}

class CellAnnotationViewer {
    func displayCellTypes(annotations: [String]) -> OmniResult<Bool> {
        if annotations.isEmpty {
            return OmniResult(value: nil, error: "No annotations to display")
        }
        
        // Native Swift rendering for bioinformatics dashboard
        print("Rendering \(annotations.count) cell type annotations...")
        return OmniResult(value: true, error: nil)
    }
}
