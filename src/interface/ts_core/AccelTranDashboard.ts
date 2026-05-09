export interface AccelTranMetrics {
    compressionRatio: number;
    activeBlocks: number;
    powerSavedWatts: number;
    throughputTokens: number;
}

export class AccelTranDashboard {
    private elementId: string;
    private canvas: HTMLCanvasElement | null = null;

    constructor(elementId: string) {
        this.elementId = elementId;
    }

    public mount(): void {
        const container = document.getElementById(this.elementId);
        if (!container) {
            throw new Error(`Container ${this.elementId} not found`);
        }
        this.canvas = document.createElement('canvas');
        this.canvas.width = 600;
        this.canvas.height = 400;
        container.appendChild(this.canvas);
    }

    public renderMetrics(metrics: AccelTranMetrics): void {
        if (!this.canvas) return;
        const ctx = this.canvas.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        ctx.fillStyle = '#1e1e1e';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        ctx.fillStyle = '#00ffcc';
        ctx.font = '20px Inter, sans-serif';
        ctx.fillText(`Hardware Sparsity Telemetry`, 20, 40);
        
        ctx.fillStyle = '#ffffff';
        ctx.font = '16px Inter, sans-serif';
        ctx.fillText(`Compression Ratio: ${(metrics.compressionRatio * 100).toFixed(2)}%`, 20, 80);
        ctx.fillText(`Active Blocks: ${metrics.activeBlocks}`, 20, 110);
        ctx.fillText(`Power Saved: ${metrics.powerSavedWatts.toFixed(1)} W`, 20, 140);
        ctx.fillText(`Throughput: ${metrics.throughputTokens} tokens/sec`, 20, 170);
    }
}
