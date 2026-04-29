import SwiftUI

// RPG diffusion generation gallery
// Bounds memory usage by strictly limiting cached images

struct OmniResult<T, E: Error> {
    let isOk: Bool
    let value: T?
    let error: E?
}

enum GalleryError: Error {
    case cacheExhausted
}

class RPGCacheManager {
    let maxMemoryBytes: Int = 1024 * 1024 * 250 // 250MB limit for iOS
    var currentMemory: Int = 0
    
    func cacheImage(sizeBytes: Int) -> OmniResult<Bool, GalleryError> {
        if currentMemory + sizeBytes > maxMemoryBytes {
            return OmniResult(isOk: false, value: nil, error: .cacheExhausted)
        }
        currentMemory += sizeBytes
        return OmniResult(isOk: true, value: true, error: nil)
    }
}
