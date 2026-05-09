// OMNI Interface Layer: Swift ARKit
import ARKit

public class OmniARKitManager {
    public let session = ARSession()
    
    public func startTracking() {
        let config = ARWorldTrackingConfiguration()
        session.run(config)
    }
}
