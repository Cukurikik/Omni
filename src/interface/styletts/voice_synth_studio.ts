// @omni-layer Interface | @omni-source sidharthrajaram/StyleTTS2 | @omni-lang TypeScript
// @omni-description Voice synthesis studio: interactive TTS interface with
// speaker selection, style transfer, and audio waveform visualization.

interface SpeakerOption {
  id: string;
  name: string;
  language: string;
  sampleUrl?: string;
}

interface SynthesisConfig {
  text: string;
  speakerId: string;
  speed: number;
  pitch: number;
  energy: number;
  styleTransfer: boolean;
  referenceSpeakerId?: string;
}

interface SynthesisResult {
  duration: number;
  melFrames: number;
  sampleRate: number;
  waveformPeaks: number[];
}

class VoiceSynthStudio {
  private container: HTMLElement;
  private speakers: SpeakerOption[] = [];
  private config: SynthesisConfig = {
    text: '', speakerId: '', speed: 1.0, pitch: 1.0, energy: 1.0, styleTransfer: false
  };
  private result: SynthesisResult | null = null;

  constructor(containerId: string) {
    const el = document.getElementById(containerId);
    if (!el) throw new Error(`Container ${containerId} not found`);
    this.container = el;
  }

  setSpeakers(speakers: SpeakerOption[]): void {
    this.speakers = speakers;
    if (speakers.length > 0) this.config.speakerId = speakers[0].id;
    this.render();
  }

  setResult(result: SynthesisResult): void {
    this.result = result;
    this.renderWaveform();
  }

  private render(): void {
    this.container.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 320px;gap:16px">
        <div>
          <div style="background:#1a1f36;border-radius:12px;padding:20px;margin-bottom:12px">
            <h3 style="color:#93c5fd;margin-bottom:12px">🎤 Text Input</h3>
            <textarea id="ttsInput" style="width:100%;min-height:120px;background:#0a0e17;color:#e2e8f0;border:1px solid #334155;border-radius:8px;padding:12px;font-size:0.9rem;resize:vertical" placeholder="Enter text to synthesize..."></textarea>
          </div>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">
            ${this.renderSlider('Speed', 'speed', 0.5, 2.0, this.config.speed)}
            ${this.renderSlider('Pitch', 'pitch', 0.5, 2.0, this.config.pitch)}
            ${this.renderSlider('Energy', 'energy', 0.5, 2.0, this.config.energy)}
          </div>
          <div id="waveformArea" style="background:#1a1f36;border-radius:12px;padding:20px;min-height:120px">
            <h3 style="color:#93c5fd;margin-bottom:12px">🔊 Waveform</h3>
            <div style="color:#64748b;font-size:0.85rem">Synthesize to view waveform</div>
          </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px">
          <div style="background:#1a1f36;border-radius:12px;padding:16px">
            <h4 style="color:#93c5fd;margin-bottom:10px">Speaker</h4>
            ${this.speakers.map(s => `
              <div style="padding:8px 10px;background:${s.id===this.config.speakerId?'#1e3a5f':'#0a0e17'};border-radius:6px;margin:4px 0;cursor:pointer;font-size:0.85rem;display:flex;justify-content:space-between">
                <span>${s.name}</span><span style="color:#64748b">${s.language}</span>
              </div>`).join('')}
          </div>
          <div style="background:#1a1f36;border-radius:12px;padding:16px">
            <h4 style="color:#93c5fd;margin-bottom:10px">Style Transfer</h4>
            <label style="display:flex;align-items:center;gap:8px;font-size:0.85rem;cursor:pointer">
              <input type="checkbox" id="styleToggle">
              <span>Enable style transfer</span>
            </label>
          </div>
          ${this.result ? this.renderResultStats() : ''}
        </div>
      </div>`;
  }

  private renderSlider(label: string, key: string, min: number, max: number, value: number): string {
    return `<div style="background:#1a1f36;border-radius:8px;padding:12px">
      <div style="font-size:0.75rem;color:#64748b;margin-bottom:4px">${label}</div>
      <div style="font-size:1.1rem;font-weight:600;color:#60a5fa">${value.toFixed(1)}x</div>
    </div>`;
  }

  private renderResultStats(): string {
    if (!this.result) return '';
    return `<div style="background:#1a1f36;border-radius:12px;padding:16px">
      <h4 style="color:#93c5fd;margin-bottom:10px">Result</h4>
      <div style="font-size:0.85rem;color:#94a3b8">
        <div>Duration: <b style="color:#60a5fa">${this.result.duration.toFixed(2)}s</b></div>
        <div>Mel Frames: <b style="color:#a78bfa">${this.result.melFrames}</b></div>
        <div>Sample Rate: <b style="color:#22d3ee">${this.result.sampleRate}Hz</b></div>
      </div>
    </div>`;
  }

  private renderWaveform(): void {
    if (!this.result) return;
    const area = document.getElementById('waveformArea');
    if (!area) return;
    const peaks = this.result.waveformPeaks || [];
    const width = 500, height = 80;
    const bars = peaks.map((p, i) => {
      const x = (i / peaks.length) * width;
      const h = Math.abs(p) * height;
      return `<rect x="${x}" y="${(height-h)/2}" width="2" height="${h}" fill="#60a5fa" rx="1"/>`;
    }).join('');
    area.innerHTML = `<h3 style="color:#93c5fd;margin-bottom:12px">🔊 Waveform</h3>
      <svg width="${width}" height="${height}" style="width:100%">${bars}</svg>`;
  }
}

export { VoiceSynthStudio, SpeakerOption, SynthesisConfig, SynthesisResult };
