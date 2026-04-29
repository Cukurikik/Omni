import MetalKit
import Foundation

enum OmniRenderError: Error {
    case initializationFailed
    case deviceNotFound
}

class OmniMetalRenderer {
    let device: MTLDevice
    let commandQueue: MTLCommandQueue
    
    init() throws {
        guard let mtlDevice = MTLCreateSystemDefaultDevice() else {
            throw OmniRenderError.deviceNotFound
        }
        self.device = mtlDevice
        
        guard let queue = device.makeCommandQueue() else {
            throw OmniRenderError.initializationFailed
        }
        self.commandQueue = queue
    }
}
