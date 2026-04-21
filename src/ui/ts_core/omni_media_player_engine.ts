/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI MEDIA PLAYER ENGINE (POLYLINGUAL REMEDIATION)
// ===========================================================================
// Absorbed From  : ReactPlayer + MediaChrome + Howler.js concepts
// Logic Inherited: TypeScript / UI Layer (Unified State Machine Player)
// Domain Layer   : UI (TypeScript Core)
// ===========================================================================
//
// By studying ReactPlayer's multi-provider abstraction and MediaChrome's
// custom element architecture, Mother learned that a unified media player
// is fundamentally a finite state machine (FSM): Idle → Loading → Ready →
// Playing → Paused → Ended, with error transitions from any state.
// TypeScript's discriminated unions enforce impossible states at compile
// time—a technique that prevents entire categories of UI bugs.

// ---- Discriminated Union State Machine ----

export type PlayerState =
  | { kind: 'idle' }
  | { kind: 'loading'; source: string }
  | { kind: 'ready'; source: string; duration: number }
  | { kind: 'playing'; source: string; duration: number; currentTime: number }
  | { kind: 'paused'; source: string; duration: number; currentTime: number }
  | { kind: 'seeking'; source: string; duration: number; targetTime: number }
  | { kind: 'buffering'; source: string; duration: number; currentTime: number }
  | { kind: 'ended'; source: string; duration: number }
  | { kind: 'error'; source: string; error: string };

// ---- Event System (Type-Safe) ----

export type PlayerEventType =
  | 'statechange'
  | 'timeupdate'
  | 'volumechange'
  | 'ratechange'
  | 'durationchange'
  | 'progress'
  | 'error';

export interface PlayerEventPayload {
  type: PlayerEventType;
  state: PlayerState;
  timestamp: number;
  detail?: Record<string, unknown>;
}

type EventHandler = (event: PlayerEventPayload) => void;

// ---- Media Source Detection ----

export type MediaType = 'audio' | 'video' | 'stream' | 'unknown';

function detectMediaType(url: string): MediaType {
  const lower = url.toLowerCase();
  const audioExts = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.opus'];
  const videoExts = ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.m3u8'];

  if (audioExts.some(ext => lower.endsWith(ext))) return 'audio';
  if (videoExts.some(ext => lower.endsWith(ext))) return 'video';
  if (lower.includes('.m3u8') || lower.includes('stream')) return 'stream';
  return 'unknown';
}

// ---- Core Engine ----

export class OmniMediaPlayerEngine {
  private state: PlayerState = { kind: 'idle' };
  private volume: number = 1.0;
  private muted: boolean = false;
  private playbackRate: number = 1.0;
  private loop: boolean = false;
  private listeners: Map<PlayerEventType, EventHandler[]> = new Map();
  private buffered: { start: number; end: number }[] = [];
  private playHistory: Array<{ source: string; playedAt: number }> = [];
  private timerId: ReturnType<typeof setInterval> | null = null;

  constructor() {
    // Initialize event listener maps
    const eventTypes: PlayerEventType[] = [
      'statechange', 'timeupdate', 'volumechange',
      'ratechange', 'durationchange', 'progress', 'error',
    ];
    for (const type of eventTypes) {
      this.listeners.set(type, []);
    }
  }

  // ---------- State Transitions ----------

  /**
   * Load a media source. Transitions: idle|paused|ended|error → loading.
   */
  load(source: string): void {
    this.transition({ kind: 'loading', source });

    // Simulate async loading (in production: attach to HTMLMediaElement)
    setTimeout(() => {
      const duration = 180 + Math.random() * 120; // 3-5 min simulated
      this.transition({ kind: 'ready', source, duration });
    }, 50);
  }

  /**
   * Start playback. Transitions: ready|paused → playing.
   */
  play(): void {
    const s = this.state;
    if (s.kind === 'ready') {
      this.transition({
        kind: 'playing',
        source: s.source,
        duration: s.duration,
        currentTime: 0,
      });
      this.startTimeUpdates();
      this.playHistory.push({ source: s.source, playedAt: Date.now() });
    } else if (s.kind === 'paused') {
      this.transition({
        kind: 'playing',
        source: s.source,
        duration: s.duration,
        currentTime: s.currentTime,
      });
      this.startTimeUpdates();
    }
  }

  /**
   * Pause playback. Transitions: playing → paused.
   */
  pause(): void {
    const s = this.state;
    if (s.kind === 'playing') {
      this.stopTimeUpdates();
      this.transition({
        kind: 'paused',
        source: s.source,
        duration: s.duration,
        currentTime: s.currentTime,
      });
    }
  }

  /**
   * Seek to a specific time. Transitions: playing|paused → seeking → playing|paused.
   */
  seek(time: number): void {
    const s = this.state;
    if (s.kind === 'playing' || s.kind === 'paused') {
      const clampedTime = Math.max(0, Math.min(time, s.duration));
      const wasPlaying = s.kind === 'playing';

      this.transition({
        kind: 'seeking',
        source: s.source,
        duration: s.duration,
        targetTime: clampedTime,
      });

      // Simulate seek completion
      setTimeout(() => {
        if (wasPlaying) {
          this.transition({
            kind: 'playing',
            source: s.source,
            duration: s.duration,
            currentTime: clampedTime,
          });
        } else {
          this.transition({
            kind: 'paused',
            source: s.source,
            duration: s.duration,
            currentTime: clampedTime,
          });
        }
      }, 20);
    }
  }

  /**
   * Stop playback and return to idle.
   */
  stop(): void {
    this.stopTimeUpdates();
    this.transition({ kind: 'idle' });
  }

  // ---------- Volume & Playback Rate ----------

  setVolume(vol: number): void {
    this.volume = Math.max(0, Math.min(1, vol));
    this.emit('volumechange');
  }

  getVolume(): number {
    return this.volume;
  }

  setMuted(muted: boolean): void {
    this.muted = muted;
    this.emit('volumechange');
  }

  isMuted(): boolean {
    return this.muted;
  }

  setPlaybackRate(rate: number): void {
    this.playbackRate = Math.max(0.25, Math.min(4.0, rate));
    this.emit('ratechange');
  }

  getPlaybackRate(): number {
    return this.playbackRate;
  }

  setLoop(loop: boolean): void {
    this.loop = loop;
  }

  // ---------- State Query ----------

  getState(): PlayerState {
    return this.state;
  }

  getCurrentTime(): number {
    const s = this.state;
    if (s.kind === 'playing' || s.kind === 'paused' || s.kind === 'buffering') {
      return s.currentTime;
    }
    return 0;
  }

  getDuration(): number {
    const s = this.state;
    if ('duration' in s) {
      return s.duration;
    }
    return 0;
  }

  getProgress(): number {
    const duration = this.getDuration();
    if (duration <= 0) return 0;
    return this.getCurrentTime() / duration;
  }

  getMediaType(): MediaType {
    const s = this.state;
    if ('source' in s) {
      return detectMediaType(s.source);
    }
    return 'unknown';
  }

  // ---------- Event System ----------

  on(type: PlayerEventType, handler: EventHandler): void {
    const handlers = this.listeners.get(type);
    if (handlers) {
      handlers.push(handler);
    }
  }

  off(type: PlayerEventType, handler: EventHandler): void {
    const handlers = this.listeners.get(type);
    if (handlers) {
      const idx = handlers.indexOf(handler);
      if (idx !== -1) handlers.splice(idx, 1);
    }
  }

  private emit(type: PlayerEventType, detail?: Record<string, unknown>): void {
    const payload: PlayerEventPayload = {
      type,
      state: this.state,
      timestamp: Date.now(),
      detail,
    };
    const handlers = this.listeners.get(type) || [];
    for (const handler of handlers) {
      try {
        handler(payload);
      } catch {
        // Event handler errors should not crash the player
      }
    }
  }

  // ---------- Internal Mechanics ----------

  private transition(newState: PlayerState): void {
    this.state = newState;
    this.emit('statechange', { kind: newState.kind });
  }

  private startTimeUpdates(): void {
    this.stopTimeUpdates();
    this.timerId = setInterval(() => {
      const s = this.state;
      if (s.kind === 'playing') {
        const newTime = s.currentTime + 0.25 * this.playbackRate;
        if (newTime >= s.duration) {
          this.stopTimeUpdates();
          if (this.loop) {
            this.transition({
              kind: 'playing',
              source: s.source,
              duration: s.duration,
              currentTime: 0,
            });
            this.startTimeUpdates();
          } else {
            this.transition({ kind: 'ended', source: s.source, duration: s.duration });
          }
        } else {
          this.state = { ...s, currentTime: newTime };
          this.emit('timeupdate');
        }
      }
    }, 250);
  }

  private stopTimeUpdates(): void {
    if (this.timerId !== null) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
  }

  // ---------- Diagnostics ----------

  diagnostics(): Record<string, unknown> {
    return {
      engine: 'OmniMediaPlayerEngine',
      layer: 'TypeScript UI',
      current_state: this.state.kind,
      volume: this.volume,
      muted: this.muted,
      playback_rate: this.playbackRate,
      loop: this.loop,
      media_type: this.getMediaType(),
      progress: Math.round(this.getProgress() * 100) / 100,
      play_history_count: this.playHistory.length,
      listener_counts: Object.fromEntries(
        Array.from(this.listeners.entries()).map(([k, v]) => [k, v.length])
      ),
      learned_logic: [
        'discriminated-union-fsm',
        'compile-time-impossible-state-prevention',
        'type-safe-event-emitter',
        'media-type-detection',
        'interval-based-time-simulation',
        'playback-rate-clamping',
      ],
    };
  }
}
