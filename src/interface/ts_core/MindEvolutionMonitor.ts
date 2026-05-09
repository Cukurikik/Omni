export interface EvolutionStat {
    generation: number;
    maxFitness: number;
    avgFitness: number;
}

export class MindEvolutionMonitor {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private history: EvolutionStat[] = [];

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = el;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public addStat(stat: EvolutionStat): void {
        this.history.push(stat);
        if (this.history.length > 50) this.history.shift();
        this.render();
    }

    private render(): void {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillStyle = '#111';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        if (this.history.length === 0) return;

        this.ctx.strokeStyle = '#00ff00'; // Max fitness line
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        const step = this.canvas.width / 50;
        
        for (let i = 0; i < this.history.length; i++) {
            const x = i * step;
            const y = this.canvas.height - (this.history[i].maxFitness * this.canvas.height);
            if (i === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
        }
        this.ctx.stroke();
        
        // UI text
        this.ctx.fillStyle = '#fff';
        this.ctx.font = '14px monospace';
        const last = this.history[this.history.length - 1];
        this.ctx.fillText(`Gen: ${last.generation} | Max Fit: ${last.maxFitness.toFixed(3)}`, 10, 20);
    }
}
