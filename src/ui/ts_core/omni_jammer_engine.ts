// ===========================================================================
// OMNI JAMMER ENGINE (SEMESTER 5 — BATCH 4)
// ===========================================================================
// Absorbed From  : jooapa/jammer
// Logic Inherited: Interface Layer (Interactive Audio Loop System)
// ===========================================================================

export interface JamTrack {
    id: string;
    bpm: number;
    loopLengthMs: number;
    isPlaying: boolean;
    volume: number;
}

export class OmniJammerEngine {
    private tracks: Map<string, JamTrack> = new Map();
    private masterBpm: number;

    constructor(bpm: number = 120) {
        this.masterBpm = bpm;
    }

    public setMasterBpm(bpm: number): { success: boolean; value?: number; error?: Error } {
        if (bpm < 20 || bpm > 300) {
            return { success: false, error: new Error("BPM must be between 20 and 300.") };
        }
        this.masterBpm = bpm;
        this.tracks.forEach(t => { t.bpm = bpm; t.loopLengthMs = (60000 / bpm) * 4; });
        return { success: true, value: bpm };
    }

    public addTrack(trackId: string): { success: boolean; value?: JamTrack; error?: Error } {
        if (this.tracks.has(trackId)) {
            return { success: false, error: new Error(`Track '${trackId}' already exists.`) };
        }
        const track: JamTrack = {
            id: trackId, bpm: this.masterBpm,
            loopLengthMs: (60000 / this.masterBpm) * 4,
            isPlaying: false, volume: 0.8
        };
        this.tracks.set(trackId, track);
        return { success: true, value: track };
    }

    public toggleTrack(trackId: string): { success: boolean; value?: boolean; error?: Error } {
        const track = this.tracks.get(trackId);
        if (!track) return { success: false, error: new Error(`Track '${trackId}' not found.`) };
        track.isPlaying = !track.isPlaying;
        return { success: true, value: track.isPlaying };
    }

    public getSessionState(): Record<string, any> {
        return {
            masterBpm: this.masterBpm,
            trackCount: this.tracks.size,
            activeTracks: Array.from(this.tracks.values()).filter(t => t.isPlaying).length
        };
    }

    public evaluateHealth(): Record<string, any> {
        return { engine: "OmniJammerEngine", layer: "Interface", status: "healthy",
                 tracks: this.tracks.size, learned_from: "jooapa/jammer" };
    }
}
