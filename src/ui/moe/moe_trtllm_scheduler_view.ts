// moe_trtllm_scheduler_view.ts — Interface Layer: TensorRT Scheduler View
// TypeScript DOM logic updating real-time tail-latency charts.

export class SchedulerView {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private dataPoints: number[] = [];

    constructor(canvasId: string) {
        this.canvas = document.getElementById(canvasId) as HTMLCanvasElement;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public updateMetric(p99LatencyMs: number) {
        this.dataPoints.push(p99LatencyMs);
        if (this.dataPoints.length > 50) {
            this.dataPoints.shift();
        }
        this.render();
    }

    private render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.beginPath();
        this.ctx.strokeStyle = '#00ff00';
        this.ctx.lineWidth = 2;

        const stepX = this.canvas.width / 50;
        const scaleY = this.canvas.height / 200; // max latency 200ms

        for (let i = 0; i < this.dataPoints.length; i++) {
            const x = i * stepX;
            const y = this.canvas.height - (this.dataPoints[i] * scaleY);
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.stroke();
    }
}
