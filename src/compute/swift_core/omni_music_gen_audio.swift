// Omni Music Gen Audio Engine (Swift)
// Compute Layer: Native Apple audio generation bounds for music synthesis.
// Ref: shaopengw/Awesome-Music-Generation

import Foundation

struct AudioLatent {
    let samples: [Double]
    let sampleRate: Int
}

func generateSineWave(frequency: Double, duration: Double, sampleRate: Int = 44100) -> AudioLatent {
    guard frequency > 0, duration > 0, sampleRate > 0 else { return AudioLatent(samples: [], sampleRate: sampleRate) }
    let n = Int(duration * Double(sampleRate))
    let samples = (0..<n).map { t in sin(2.0 * .pi * frequency * Double(t) / Double(sampleRate)) }
    return AudioLatent(samples: samples, sampleRate: sampleRate)
}
