// moe_lixaudio_waveform.ts — Interface
// Layer: Interface — Lixaudio Waveform Renderer
// Inspired by: lixaudio (Smart audio pipeline)

export class WaveformRenderer {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error("Canvas element not found");
        
        this.canvas = el;
        this.ctx = el.getContext('2d')!;
    }

    // Zero-copy rendering directly from Float32Array from AudioContext
    public drawWaveform(audioData: Float32Array) {
        const width = this.canvas.width;
        const height = this.canvas.height;
        const step = Math.ceil(audioData.length / width);
        
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, width, height);
        
        this.ctx.lineWidth = 1;
        this.ctx.strokeStyle = '#00ffcc';
        this.ctx.beginPath();

        for (let i = 0; i < width; i++) {
            let min = 1.0;
            let max = -1.0;
            for (let j = 0; j < step; j++) {
                const datum = audioData[(i * step) + j];
                if (datum < min) min = datum;
                if (datum > max) max = datum;
            }
            
            const y1 = (1 + min) * height / 2;
            const y2 = (1 + max) * height / 2;
            
            this.ctx.moveTo(i, y1);
            this.ctx.lineTo(i, y2);
        }
        
        this.ctx.stroke();
    }
}
