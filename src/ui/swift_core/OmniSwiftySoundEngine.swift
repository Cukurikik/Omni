//
//  OmniSwiftySoundEngine.swift
//  Production-Grade Apple UI Audio State Management
//  ================================================
//  Absorbed from: SwiftySound
//
//  Key patterns learned and implemented:
//  - AVAudioPlayer caching and simple extraction
//  - Global category management mapping directly to AVAudioSession
//  - Looping functionality and deterministic muting
//  - Apple ecosystem memory-safe instance mapping
//
//  OMNI Layer: ui/swift_core
//  @since 2026.4.0
//

import Foundation
import AVFoundation

public enum SoundError: Error {
    case fileNotFound(String)
    case engineFailure(String)
}

/// Monadic Result wrapper preventing raw Swift `throw` traces in production.
public enum SoundResult<T> {
    case ok(T)
    case err(SoundError)
    
    public func unwrap() throws -> T {
        switch self {
        case .ok(let value): return value
        case .err(let err): throw err
        }
    }
    
    public var isOk: Bool {
        if case .ok = self { return true }
        return false
    }
}

/// Global session management matching SwiftySound's category capabilities
public enum SoundCategory {
    case ambient
    case playback
    case record
    case playAndRecord
    
    internal var avCategory: AVAudioSession.Category {
        switch self {
        case .ambient: return .ambient
        case .playback: return .playback
        case .record: return .record
        case .playAndRecord: return .playAndRecord
        }
    }
}

public class OmniSwiftySoundEngine {
    
    // Maintain active references to prevent ARC deallocation during playback
    private var activePlayers: [URL: AVAudioPlayer] = [:]
    
    public static let shared = OmniSwiftySoundEngine()
    
    private init() {}
    
    /// Global muting switch
    public var isMuted: Bool = false {
        didSet {
            for player in activePlayers.values {
                player.volume = isMuted ? 0.0 : 1.0
            }
        }
    }
    
    /// Sets global AV session category smoothly.
    public func setCategory(_ category: SoundCategory) -> SoundResult<Bool> {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(category.avCategory, mode: .default, options: [])
            try session.setActive(true, options: [])
            return .ok(true)
        } catch {
            return .err(.engineFailure("Failed to configure AVAudioSession: \(error.localizedDescription)"))
        }
    }
    
    /// Retrieves or spawns an AVAudioPlayer, caching it strictly to avoid disk re-reads.
    private func fetchPlayer(for url: URL) -> SoundResult<AVAudioPlayer> {
        if let cached = activePlayers[url] {
            return .ok(cached)
        }
        
        do {
            let player = try AVAudioPlayer(contentsOf: url)
            player.prepareToPlay()
            activePlayers[url] = player
            return .ok(player)
        } catch {
            return .err(.engineFailure("Failed decoding audio payload: \(error.localizedDescription)"))
        }
    }
    
    /// Production playback method handling muting, looping, and invocation
    public func play(fileURL: URL, loops: Int = 0) -> SoundResult<Bool> {
        let fetchRes = fetchPlayer(for: fileURL)
        switch fetchRes {
        case .err(let err): return .err(err)
        case .ok(let player):
            player.numberOfLoops = loops
            player.volume = isMuted ? 0.0 : 1.0
            
            if !player.isPlaying {
                player.play()
            }
            return .ok(true)
        }
    }
    
    /// Instantly pauses active player for strict URL
    public func pause(fileURL: URL) -> SoundResult<Bool> {
        guard let player = activePlayers[fileURL] else {
            return .err(.fileNotFound("No active player registered for URL"))
        }
        player.pause()
        return .ok(true)
    }
    
    /// Stops and frees ARC reference caching logic explicitly
    public func stopAndClear(fileURL: URL) -> SoundResult<Bool> {
        guard let player = activePlayers[fileURL] else {
            return .ok(true)
        }
        player.stop()
        activePlayers.removeValue(forKey: fileURL)
        return .ok(true)
    }
}
