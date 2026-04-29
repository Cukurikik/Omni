/// <reference lib="dom" />
/// <reference types="node" />
/**
 * OmniReactMusicPlayerEngine.ts
 * Production-Grade Abstract Playlist State Topology
 * ==============================================================
 * Absorbed from: lijinke666/react-music-player
 *
 * Key patterns learned and implemented:
 * - Drops heavy React component hooks evaluating absolute class structures routing playback streams natively.
 * - Simulates explicit state mutation bounds modeling synchronous unmanaged UI state flows explicitly.
 * - Extracts discrete track looping geometries isolating DOM representations effortlessly transparently.
 *
 * OMNI Layer: ui/typescript_core
 * @since 2026.4.0
 */

export const ENGINE_VERSION = "1.0.0-omni";

// --- Monadic Error Definition ---

export enum PlayerError {
    TRACK_NOT_FOUND = "TRACK_NOT_FOUND",
    PLAYLIST_EXHAUSTED = "PLAYLIST_EXHAUSTED"
}

export type PlayerResult<T> = 
    | { isOk: true; value: T }
    | { isOk: false; error: PlayerError };

export const Ok = <T>(value: T): PlayerResult<T> => ({ isOk: true, value });
export const Err = <T>(error: PlayerError): PlayerResult<T> => ({ isOk: false, error });

export interface TrackData {
    id: string;
    name: string;
    src: string;
}

export class OmniReactMusicPlayerEngine {
    private playlist: TrackData[];
    private currentIndex: number;
    private isPlaying: boolean;

    constructor() {
        this.playlist = [];
        this.currentIndex = -1;
        this.isPlaying = false;
    }

    /**
     * Binds native playlist structures safely avoiding UI array-key React loops internally correctly mapping items natively.
     */
    public initializePlaylist(tracks: TrackData[]): PlayerResult<boolean> {
        if (!tracks || tracks.length === 0) {
            return Err(PlayerError.TRACK_NOT_FOUND);
        }
        this.playlist = [...tracks];
        this.currentIndex = 0;
        return Ok(true);
    }

    public playNext(): PlayerResult<TrackData> {
        if (this.playlist.length === 0) {
            return Err(PlayerError.PLAYLIST_EXHAUSTED);
        }

        // Circular loop boundary organically executing decoupled from React state-closures cleanly!
        this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
        this.isPlaying = true;

        return Ok(this.playlist[this.currentIndex]);
    }

    public playPrevious(): PlayerResult<TrackData> {
        if (this.playlist.length === 0) {
            return Err(PlayerError.PLAYLIST_EXHAUSTED);
        }

        this.currentIndex = (this.currentIndex - 1 + this.playlist.length) % this.playlist.length;
        this.isPlaying = true;

        return Ok(this.playlist[this.currentIndex]);
    }

    public getActiveState(): Record<string, any> {
        return {
            playing: this.isPlaying,
            active_track: this.currentIndex >= 0 ? this.playlist[this.currentIndex].id : null,
            total_tracks: this.playlist.length,
            version: ENGINE_VERSION
        };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniReactMusicPlayerEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
