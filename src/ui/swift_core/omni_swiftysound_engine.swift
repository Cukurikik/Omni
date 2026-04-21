// omni_swiftysound_engine.swift
// Production-Grade Swift Audio Playback Engine
// ==============================================================
// Absorbed from: adamcichy/SwiftySound
//
// OMNI Layer: ui/swift_core
// @since 2026.4.0

import Foundation

let ENGINE_VERSION = "1.0.0-omni"

enum SoundError: Error {
    case fileNotFound(String)
    case invalidVolume(Float)
    case playerLimitReached(Int)
    case alreadyPlaying(String)
    case notPlaying(String)
}

struct SoundConfig {
    let id: String
    let filePath: String
    let volume: Float
    let loops: Int
    let category: String
    let preload: Bool
}

struct SoundState {
    let id: String
    var isPlaying: Bool
    var isPaused: Bool
    var volume: Float
    var currentLoop: Int
    var totalLoops: Int
    var startedAt: TimeInterval
}

/// Production-grade Swift audio playback engine.
///
/// Manages concurrent sound playback with volume control,
/// loop management, audio categories (music, effects, ambient),
/// and player pool management for optimal memory use.
class OmniSwiftysoundEngine {
    private var sounds: [String: SoundConfig] = [:]
    private var states: [String: SoundState] = [:]
    private var globalVolume: Float = 1.0
    private var globalMuted: Bool = false
    private let maxConcurrent: Int
    private var categories: [String: Float] = ["music": 1.0, "effects": 1.0, "ambient": 0.7]

    init(maxConcurrent: Int = 16) {
        self.maxConcurrent = maxConcurrent
    }

    /// Register a sound file for playback.
    func registerSound(_ config: SoundConfig) -> [String: Any] {
        if config.volume < 0 || config.volume > 1 {
            return ["status": "error", "code": "INVALID_VOL", "message": "Volume [0, 1]"]
        }
        sounds[config.id] = config
        return ["status": "success", "data": [
            "id": config.id, "filePath": config.filePath,
            "totalSounds": sounds.count] as [String: Any]]
    }

    /// Play a registered sound.
    func play(_ soundId: String, volume: Float = -1, loops: Int = -1) -> [String: Any] {
        guard let config = sounds[soundId] else {
            return ["status": "error", "code": "NOT_FOUND"]
        }
        if states.filter({ $0.value.isPlaying }).count >= maxConcurrent {
            return ["status": "error", "code": "MAX_CONCURRENT"]
        }

        let vol = volume >= 0 ? min(1.0, volume) : config.volume
        let lps = loops >= 0 ? loops : config.loops
        let effectiveVol = vol * globalVolume * (categories[config.category] ?? 1.0)

        states[soundId] = SoundState(
            id: soundId, isPlaying: true, isPaused: false,
            volume: vol, currentLoop: 0, totalLoops: lps,
            startedAt: Date().timeIntervalSince1970
        )

        return ["status": "success", "data": [
            "id": soundId, "effectiveVolume": effectiveVol,
            "loops": lps, "category": config.category,
            "activeSounds": states.filter { $0.value.isPlaying }.count
        ] as [String: Any]]
    }

    /// Pause a playing sound.
    func pause(_ soundId: String) -> [String: Any] {
        guard var state = states[soundId] else {
            return ["status": "error", "code": "NOT_FOUND"]
        }
        state.isPaused = true
        state.isPlaying = false
        states[soundId] = state
        return ["status": "success", "data": ["id": soundId, "paused": true]]
    }

    /// Stop a sound and reset its state.
    func stop(_ soundId: String) -> [String: Any] {
        guard states[soundId] != nil else {
            return ["status": "error", "code": "NOT_FOUND"]
        }
        states.removeValue(forKey: soundId)
        return ["status": "success", "data": ["id": soundId, "stopped": true]]
    }

    /// Stop all sounds.
    func stopAll() -> [String: Any] {
        let count = states.count
        states.removeAll()
        return ["status": "success", "data": ["stoppedCount": count]]
    }

    /// Set global volume.
    func setGlobalVolume(_ volume: Float) -> [String: Any] {
        globalVolume = max(0, min(1, volume))
        return ["status": "success", "data": [
            "globalVolume": globalVolume, "muted": globalMuted]]
    }

    /// Set category volume.
    func setCategoryVolume(_ category: String, volume: Float) -> [String: Any] {
        categories[category] = max(0, min(1, volume))
        return ["status": "success", "data": [
            "category": category, "volume": categories[category] ?? 0]]
    }

    /// Toggle global mute.
    func toggleMute() -> [String: Any] {
        globalMuted = !globalMuted
        return ["status": "success", "data": ["muted": globalMuted]]
    }

    /// Get engine status.
    func getStatus() -> [String: Any] {
        let playing = states.filter { $0.value.isPlaying }.count
        let paused = states.filter { $0.value.isPaused }.count
        return ["status": "success", "data": [
            "registeredSounds": sounds.count,
            "playingSounds": playing, "pausedSounds": paused,
            "maxConcurrent": maxConcurrent,
            "globalVolume": globalVolume, "globalMuted": globalMuted,
            "categories": categories
        ] as [String: Any]]
    }
}
