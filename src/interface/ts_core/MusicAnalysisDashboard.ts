export interface MusicTag {
    label: string;
    probability: number;
}

export class MusicAnalysisDashboard {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = el;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public renderAnalysis(tags: MusicTag[], tempo: number, waveform: number[]): void {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Background
        this.ctx.fillStyle = '#0a0a0a';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Waveform
        this.ctx.strokeStyle = '#00ffaa';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        const step = this.canvas.width / waveform.length;
        for(let i=0; i<waveform.length; i++) {
            const x = i * step;
            const y = (this.canvas.height / 2) + (waveform[i] * 50);
            if(i === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
        }
        this.ctx.stroke();

        // Info
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '16px Inter';
        this.ctx.fillText(`Detected Tempo: ${tempo.toFixed(1)} BPM`, 20, 30);
        
        let yOffset = 60;
        for(const tag of tags) {
            this.ctx.fillText(`${tag.label}: ${(tag.probability * 100).toFixed(1)}%`, 20, yOffset);
            yOffset += 25;
        }
    }
}
