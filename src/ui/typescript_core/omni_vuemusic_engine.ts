/// <reference lib="dom" />
/// <reference types="node" />
// omni_vuemusic_engine.ts
// Production-Grade Vue.js Music Component Engine
// ==============================================================
// Absorbed from: k-water/vue-music
//
// OMNI Layer: ui/typescript_core
// @since 2026.4.0

const ENGINE_VERSION = "1.0.0-omni";

interface Song { id: string; title: string; artist: string; album: string; durationMs: number; cover?: string; }
interface PlayerState { isPlaying: boolean; currentSong: Song | null; position: number; volume: number; mode: PlayMode; }
type PlayMode = "sequence" | "random" | "loop_one" | "loop_all";

class VueMusicError extends Error {
    constructor(public code: string, msg: string) { super(msg); this.name = "VueMusicError"; }
}

/**
 * Production-grade Vue.js music component state engine.
 * Manages song lists, playback modes, favorites, lyrics sync, and search.
 */
export class OmniVuemusicEngine {
    private songs: Song[] = [];
    private favorites: Set<string> = new Set();
    private recentlyPlayed: Song[] = [];
    private currentIndex: number = -1;
    private isPlaying: boolean = false;
    private position: number = 0;
    private volume: number = 0.8;
    private mode: PlayMode = "sequence";
    private maxRecent: number = 50;

    /** Load a song library. */
    loadLibrary(songs: Song[]): { status: string; data: { loaded: number; totalDurationMs: number } } {
        if (!songs.length) throw new VueMusicError("EMPTY", "No songs provided");
        this.songs = [...songs];
        const totalDuration = songs.reduce((a, s) => a + s.durationMs, 0);
        return { status: "success", data: { loaded: songs.length, totalDurationMs: totalDuration } };
    }

    /** Play a song by ID. */
    playSong(songId: string): { status: string; data: PlayerState } {
        const idx = this.songs.findIndex(s => s.id === songId);
        if (idx === -1) throw new VueMusicError("NOT_FOUND", `Song '${songId}' not found`);
        this.currentIndex = idx;
        this.isPlaying = true;
        this.position = 0;
        this._addRecent(this.songs[idx]);
        return { status: "success", data: this._state() };
    }

    /** Toggle play/pause. */
    togglePlay(): { status: string; data: PlayerState } {
        if (this.currentIndex < 0) throw new VueMusicError("NO_SONG", "No song selected");
        this.isPlaying = !this.isPlaying;
        return { status: "success", data: this._state() };
    }

    /** Skip to next song based on play mode. */
    nextSong(): { status: string; data: PlayerState } {
        if (!this.songs.length) throw new VueMusicError("EMPTY", "Library empty");
        if (this.mode === "random") {
            this.currentIndex = Math.floor(Math.random() * this.songs.length);
        } else if (this.mode === "loop_one") {
            // stay on same
        } else {
            this.currentIndex = (this.currentIndex + 1) % this.songs.length;
        }
        this.position = 0;
        this.isPlaying = true;
        this._addRecent(this.songs[this.currentIndex]);
        return { status: "success", data: this._state() };
    }

    /** Previous song or restart. */
    prevSong(): { status: string; data: PlayerState } {
        if (!this.songs.length) throw new VueMusicError("EMPTY", "Library empty");
        if (this.position > 3000) { this.position = 0; }
        else { this.currentIndex = this.currentIndex > 0 ? this.currentIndex - 1 : this.songs.length - 1; this.position = 0; }
        this.isPlaying = true;
        return { status: "success", data: this._state() };
    }

    /** Toggle favorite status of a song. */
    toggleFavorite(songId: string): { status: string; data: { isFavorite: boolean; totalFavorites: number } } {
        if (this.favorites.has(songId)) this.favorites.delete(songId);
        else this.favorites.add(songId);
        return { status: "success", data: { isFavorite: this.favorites.has(songId), totalFavorites: this.favorites.size } };
    }

    /** Search songs by title or artist. */
    search(query: string): { status: string; data: { results: Song[]; count: number } } {
        const q = query.toLowerCase();
        const results = this.songs.filter(s => s.title.toLowerCase().includes(q) || s.artist.toLowerCase().includes(q));
        return { status: "success", data: { results, count: results.length } };
    }

    /** Set play mode. */
    setMode(mode: PlayMode): { status: string; data: { mode: PlayMode } } {
        this.mode = mode;
        return { status: "success", data: { mode } };
    }

    /** Get recently played songs. */
    getRecentlyPlayed(): { status: string; data: { songs: Song[]; count: number } } {
        return { status: "success", data: { songs: [...this.recentlyPlayed], count: this.recentlyPlayed.length } };
    }

    /** Get all favorites. */
    getFavorites(): { status: string; data: { songs: Song[]; count: number } } {
        const favSongs = this.songs.filter(s => this.favorites.has(s.id));
        return { status: "success", data: { songs: favSongs, count: favSongs.length } };
    }

    /** Compute lyrics sync points from timestamp pairs. */
    computeLyricSync(lyrics: Array<{ timeMs: number; text: string }>, currentMs: number): {
        status: string; data: { currentLine: string; lineIndex: number; progress: number };
    } {
        let lineIndex = 0;
        for (let i = lyrics.length - 1; i >= 0; i--) {
            if (currentMs >= lyrics[i].timeMs) { lineIndex = i; break; }
        }
        const nextTime = lineIndex + 1 < lyrics.length ? lyrics[lineIndex + 1].timeMs : lyrics[lineIndex].timeMs + 5000;
        const lineProgress = Math.min(1, (currentMs - lyrics[lineIndex].timeMs) / (nextTime - lyrics[lineIndex].timeMs));
        return { status: "success", data: { currentLine: lyrics[lineIndex].text, lineIndex, progress: Math.round(lineProgress * 1000) / 1000 } };
    }

    private _state(): PlayerState {
        return { isPlaying: this.isPlaying, currentSong: this.currentIndex >= 0 ? this.songs[this.currentIndex] : null, position: this.position, volume: this.volume, mode: this.mode };
    }

    private _addRecent(song: Song): void {
        this.recentlyPlayed = [song, ...this.recentlyPlayed.filter(s => s.id !== song.id)].slice(0, this.maxRecent);
    }
}
