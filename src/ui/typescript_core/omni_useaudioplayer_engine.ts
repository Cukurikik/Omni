/// <reference lib="dom" />
/// <reference types="node" />
// omni_useaudioplayer_engine.ts
// Production-Grade React Audio Hook Engine
// ==============================================================
// Absorbed from: E-Kuerschner/useAudioPlayer
//
// OMNI Layer: ui/typescript_core
// @since 2026.4.0

const ENGINE_VERSION = "1.0.0-omni";

type PlayerPhase = "idle" | "loading" | "ready" | "playing" | "paused" | "ended" | "error";

interface AudioSource { id: string; url: string; title: string; duration: number; }
interface QueueState { current: number; total: number; loopMode: "none" | "one" | "all"; shuffle: boolean; }

class AudioPlayerError extends Error {
    constructor(public code: string, msg: string) { super(msg); this.name = "AudioPlayerError"; }
}

/**
 * Production-grade React audio player hook engine.
 * Manages playlist queue, playback state, volume, and scrubbing.
 */
export class OmniUseaudioplayerEngine {
    private phase: PlayerPhase = "idle";
    private playlist: AudioSource[] = [];
    private currentIndex: number = -1;
    private position: number = 0;
    private volume: number = 1.0;
    private muted: boolean = false;
    private loopMode: "none" | "one" | "all" = "none";
    private shuffled: boolean = false;
    private shuffleOrder: number[] = [];

    /** Load a playlist of audio sources. */
    loadPlaylist(sources: AudioSource[]): { status: string; data: QueueState } {
        if (!sources.length) throw new AudioPlayerError("EMPTY_PLAYLIST", "No sources provided");
        this.playlist = [...sources];
        this.currentIndex = 0;
        this.phase = "ready";
        this.position = 0;
        this.shuffleOrder = sources.map((_, i) => i);
        return { status: "success", data: this._queueState() };
    }

    /** Start playback of current track. */
    play(): { status: string; data: { phase: PlayerPhase; trackId: string } } {
        if (this.currentIndex < 0 || !this.playlist.length) {
            throw new AudioPlayerError("NO_TRACK", "No track loaded");
        }
        this.phase = "playing";
        return { status: "success", data: { phase: this.phase, trackId: this.playlist[this._resolveIndex()].id } };
    }

    /** Pause playback. */
    pause(): { status: string; data: { phase: PlayerPhase } } {
        if (this.phase !== "playing") throw new AudioPlayerError("NOT_PLAYING", "Cannot pause");
        this.phase = "paused";
        return { status: "success", data: { phase: this.phase } };
    }

    /** Skip to next track. */
    next(): { status: string; data: { trackId: string; index: number } } {
        if (!this.playlist.length) throw new AudioPlayerError("EMPTY", "No playlist");
        this.currentIndex++;
        if (this.currentIndex >= this.playlist.length) {
            this.currentIndex = this.loopMode === "all" ? 0 : this.playlist.length - 1;
            if (this.loopMode !== "all") { this.phase = "ended"; }
        }
        this.position = 0;
        const idx = this._resolveIndex();
        return { status: "success", data: { trackId: this.playlist[idx].id, index: idx } };
    }

    /** Skip to previous track. */
    previous(): { status: string; data: { trackId: string; index: number } } {
        if (!this.playlist.length) throw new AudioPlayerError("EMPTY", "No playlist");
        if (this.position > 3000) { this.position = 0; }
        else {
            this.currentIndex = Math.max(0, this.currentIndex - 1);
            this.position = 0;
        }
        const idx = this._resolveIndex();
        return { status: "success", data: { trackId: this.playlist[idx].id, index: idx } };
    }

    /** Seek to position in milliseconds. */
    seekTo(ms: number): { status: string; data: { position: number } } {
        if (ms < 0) throw new AudioPlayerError("INVALID_SEEK", "Position must be >= 0");
        this.position = ms;
        return { status: "success", data: { position: this.position } };
    }

    /** Set volume level [0, 1]. */
    setVolume(v: number): { status: string; data: { volume: number; muted: boolean } } {
        if (v < 0 || v > 1) throw new AudioPlayerError("INVALID_VOL", `Volume [0,1], got ${v}`);
        this.volume = v;
        return { status: "success", data: { volume: this.volume, muted: this.muted } };
    }

    /** Toggle mute. */
    toggleMute(): { status: string; data: { muted: boolean } } {
        this.muted = !this.muted;
        return { status: "success", data: { muted: this.muted } };
    }

    /** Set loop mode. */
    setLoopMode(mode: "none" | "one" | "all"): { status: string; data: QueueState } {
        this.loopMode = mode;
        return { status: "success", data: this._queueState() };
    }

    /** Toggle shuffle. */
    toggleShuffle(): { status: string; data: { shuffle: boolean; order: number[] } } {
        this.shuffled = !this.shuffled;
        if (this.shuffled) {
            this.shuffleOrder = this.playlist.map((_, i) => i);
            for (let i = this.shuffleOrder.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [this.shuffleOrder[i], this.shuffleOrder[j]] = [this.shuffleOrder[j], this.shuffleOrder[i]];
            }
        } else {
            this.shuffleOrder = this.playlist.map((_, i) => i);
        }
        return { status: "success", data: { shuffle: this.shuffled, order: this.shuffleOrder } };
    }

    /** Get full player state snapshot. */
    getSnapshot(): {
        phase: PlayerPhase; currentTrack: AudioSource | null; position: number;
        volume: number; muted: boolean; queue: QueueState;
    } {
        const idx = this._resolveIndex();
        return {
            phase: this.phase,
            currentTrack: idx >= 0 && idx < this.playlist.length ? this.playlist[idx] : null,
            position: this.position,
            volume: this.muted ? 0 : this.volume,
            muted: this.muted,
            queue: this._queueState(),
        };
    }

    private _resolveIndex(): number {
        if (this.currentIndex < 0) return -1;
        return this.shuffled ? this.shuffleOrder[this.currentIndex % this.shuffleOrder.length] : this.currentIndex;
    }

    private _queueState(): QueueState {
        return { current: this.currentIndex, total: this.playlist.length, loopMode: this.loopMode, shuffle: this.shuffled };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniUseaudioplayerEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
