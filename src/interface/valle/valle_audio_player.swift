// OMNI Interface Layer: valle_audio_player.swift
// Native iOS AVFoundation player for VALL-E zero-shot TTS output.
// Bounds: Max 3 audio buffers loaded to prevent memory pressure.

import AVFoundation

struct OmniError: Error {
    let code: Int
    let message: String
}

struct OmniResult<T> {
    let data: T?
    let error: OmniError?
}

class ValleAudioPlayer {
    let maxQueuedBuffers = 3
    private var queuedCount = 0
    private let audioEngine = AVAudioEngine()
    private let playerNode = AVAudioPlayerNode()
    
    init() {
        audioEngine.attach(playerNode)
        audioEngine.connect(playerNode, to: audioEngine.mainMixerNode, format: nil)
        try? audioEngine.start()
    }
    
    func queuePcmBuffer(buffer: AVAudioPCMBuffer) -> OmniResult<Bool> {
        if queuedCount >= maxQueuedBuffers {
            return OmniResult(data: nil, error: OmniError(code: 1, message: "Exceeded 3 queued buffer bound."))
        }
        
        queuedCount += 1
        playerNode.scheduleBuffer(buffer, completionHandler: {
            DispatchQueue.main.async {
                self.queuedCount -= 1
            }
        })
        
        if !playerNode.isPlaying {
            playerNode.play()
        }
        
        return OmniResult(data: true, error: nil)
    }
}
