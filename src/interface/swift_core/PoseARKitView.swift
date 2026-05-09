import ARKit
import SceneKit

public class PoseARKitView: ARSCNView {
    public func updateSkeleton(joints: [SCNVector3]) {
        guard joints.count == 17 else { return }
        // ARKit skeleton mapping logic
    }
}
