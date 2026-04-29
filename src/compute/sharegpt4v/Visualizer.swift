import Foundation

public class Visualizer {
    public func renderCaption(caption: String) -> Result<Bool, Error> {
        if caption.isEmpty {
            return .failure(NSError(domain: "EmptyCaption", code: 400, userInfo: nil))
        }
        return .success(true)
    }
}
