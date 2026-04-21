/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI WAVEFORM VISUALIZER ENGINE (POLYLINGUAL REMEDIATION)
// ===========================================================================
// Absorbed From  : wavesurfer.js + audiowaveform + Howler.js display concepts
// Logic Inherited: TypeScript / UI Layer (Canvas-Based Waveform Renderer)
// Domain Layer   : UI (TypeScript Core)
// ===========================================================================
//
// By studying wavesurfer.js's rendering pipeline, Mother learned that
// waveform visualization reduces to: take N PCM samples → downsample to
// pixel-width bins (computing min/max per bin) → draw vertical bars on
// a canvas. TypeScript's typed arrays (Float32Array) provide the same
// zero-copy buffer access as C, while the Canvas API gives GPU-accelerated
// rendering—the best of both worlds for UI-layer visualization.

// ---- Types & Interfaces ----

export interface WaveformConfig {
  width: number;
  height: number;
  barWidth: number;
  barGap: number;
  waveColor: string;
  progressColor: string;
  backgroundColor: string;
  cursorColor: string;
  cursorWidth: number;
  responsive: boolean;
  normalize: boolean;
}

export interface WaveformBin {
  min: number;
  max: number;
  rms: number;
}

export interface RenderState {
  progress: number;        // 0.0 to 1.0
  isPlaying: boolean;
  zoomLevel: number;       // 1.0 = default, >1 = zoomed in
  scrollOffset: number;    // Horizontal scroll in bins
  cursorPosition: number;  // 0.0 to 1.0
}

// ---- Default Configuration ----

const DEFAULT_CONFIG: WaveformConfig = {
  width: 800,
  height: 128,
  barWidth: 2,
  barGap: 1,
  waveColor: '#4a9eff',
  progressColor: '#1a6dff',
  backgroundColor: '#0a0a0a',
  cursorColor: '#ff4444',
  cursorWidth: 2,
  responsive: true,
  normalize: true,
};

// ---- Core Engine ----

export class OmniWaveformVisualizerEngine {
  private config: WaveformConfig;
  private bins: WaveformBin[] = [];
  private rawPeaks: Float32Array = new Float32Array(0);
  private state: RenderState;
  private peakCache: Map<string, WaveformBin[]> = new Map();

  constructor(config: Partial<WaveformConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
    this.state = {
      progress: 0,
      isPlaying: false,
      zoomLevel: 1.0,
      scrollOffset: 0,
      cursorPosition: 0,
    };
  }

  // ---------- Data Processing ----------

  /**
   * Load PCM sample data and compute display bins.
   * This is the core downsampling algorithm from wavesurfer.js:
   * For each pixel-width column, find the min/max/RMS of all samples
   * that fall within that column's range.
   */
  loadPCMData(samples: Float32Array): void {
    this.rawPeaks = samples;
    this.bins = this.computeBins(samples);
  }

  /**
   * Downsample PCM data into display bins for the configured width.
   * Each bin spans (totalSamples / numBins) raw samples.
   */
  private computeBins(samples: Float32Array): WaveformBin[] {
    const numBins = this.calculateNumBins();
    const samplesPerBin = Math.max(1, Math.floor(samples.length / numBins));
    const bins: WaveformBin[] = [];

    // Find global peak for normalization
    let globalPeak = 0;
    if (this.config.normalize) {
      for (let i = 0; i < samples.length; i++) {
        const abs = Math.abs(samples[i]);
        if (abs > globalPeak) globalPeak = abs;
      }
    }
    const normFactor = globalPeak > 0 ? 1.0 / globalPeak : 1.0;

    for (let b = 0; b < numBins; b++) {
      const start = b * samplesPerBin;
      const end = Math.min(start + samplesPerBin, samples.length);

      let min = Infinity;
      let max = -Infinity;
      let sumSq = 0;

      for (let i = start; i < end; i++) {
        const s = samples[i] * (this.config.normalize ? normFactor : 1.0);
        if (s < min) min = s;
        if (s > max) max = s;
        sumSq += s * s;
      }

      const rms = Math.sqrt(sumSq / Math.max(1, end - start));

      bins.push({
        min: isFinite(min) ? min : 0,
        max: isFinite(max) ? max : 0,
        rms,
      });
    }

    return bins;
  }

  /** Calculate number of renderable bins based on width and bar config. */
  private calculateNumBins(): number {
    const { width, barWidth, barGap } = this.config;
    return Math.floor(width / (barWidth + barGap));
  }

  // ---------- Canvas Rendering ----------

  /**
   * Render the waveform to a 2D canvas rendering context.
   * Draws: background → wave bars → progress overlay → cursor line.
   */
  render(ctx: CanvasRenderingContext2D): void {
    const { width, height, backgroundColor } = this.config;

    // 1. Clear canvas with background color
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, width, height);

    if (this.bins.length === 0) return;

    // 2. Determine visible range (for zoom/scroll)
    const visibleBins = Math.floor(this.bins.length / this.state.zoomLevel);
    const startBin = Math.min(
      this.state.scrollOffset,
      Math.max(0, this.bins.length - visibleBins)
    );
    const endBin = Math.min(startBin + visibleBins, this.bins.length);

    // 3. Draw each bar
    const { barWidth, barGap, waveColor, progressColor } = this.config;
    const centerY = height / 2;
    const progressBin = startBin + (endBin - startBin) * this.state.progress;

    for (let i = startBin; i < endBin; i++) {
      const bin = this.bins[i];
      const x = (i - startBin) * (barWidth + barGap);

      // Bar height from min/max (symmetric around center)
      const topY = centerY - bin.max * centerY;
      const bottomY = centerY - bin.min * centerY;
      const barHeight = Math.max(1, bottomY - topY);

      // Color: progress color if before playhead, wave color otherwise
      ctx.fillStyle = i < progressBin ? progressColor : waveColor;
      ctx.fillRect(x, topY, barWidth, barHeight);
    }

    // 4. Draw cursor
    this.renderCursor(ctx, startBin, endBin);
  }

  /** Draw the playhead cursor line. */
  private renderCursor(
    ctx: CanvasRenderingContext2D,
    startBin: number,
    endBin: number
  ): void {
    const { height, barWidth, barGap, cursorColor, cursorWidth } = this.config;
    const binsVisible = endBin - startBin;
    const cursorX = this.state.cursorPosition * binsVisible * (barWidth + barGap);

    ctx.fillStyle = cursorColor;
    ctx.fillRect(cursorX - cursorWidth / 2, 0, cursorWidth, height);
  }

  // ---------- State Management ----------

  setProgress(progress: number): void {
    this.state.progress = Math.max(0, Math.min(1, progress));
    this.state.cursorPosition = this.state.progress;
  }

  setZoom(level: number): void {
    this.state.zoomLevel = Math.max(1, Math.min(100, level));
  }

  setScroll(offset: number): void {
    this.state.scrollOffset = Math.max(0, Math.floor(offset));
  }

  setPlaying(playing: boolean): void {
    this.state.isPlaying = playing;
  }

  getState(): RenderState {
    return { ...this.state };
  }

  getBinCount(): number {
    return this.bins.length;
  }

  // ---------- Export ----------

  /** Export bins as JSON for external consumers. */
  exportBins(): WaveformBin[] {
    return [...this.bins];
  }

  /** Export peaks as a compact Float32Array (max values only). */
  exportPeaks(): Float32Array {
    const peaks = new Float32Array(this.bins.length);
    for (let i = 0; i < this.bins.length; i++) {
      peaks[i] = this.bins[i].max;
    }
    return peaks;
  }

  // ---------- Diagnostics ----------

  diagnostics(): Record<string, unknown> {
    return {
      engine: 'OmniWaveformVisualizerEngine',
      layer: 'TypeScript UI',
      bins_computed: this.bins.length,
      raw_samples: this.rawPeaks.length,
      config: this.config,
      state: this.state,
      peak_cache_entries: this.peakCache.size,
      learned_logic: [
        'pcm-to-bin-downsampling',
        'min-max-rms-peak-detection',
        'canvas-bar-rendering',
        'zoom-scroll-viewport',
        'progress-overlay-coloring',
        'float32array-typed-buffer',
      ],
    };
  }
}
