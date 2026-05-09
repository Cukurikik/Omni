export interface SwarmAgent {
    id: number;
    x: number;
    y: number;
    battery: number;
}

export class SwarmArenaCanvas {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = el;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public renderFrame(agents: SwarmAgent[]): void {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Background
        this.ctx.fillStyle = '#222';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Center Coordinate System
        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        
        this.ctx.strokeStyle = '#444';
        this.ctx.beginPath();
        this.ctx.moveTo(0, cy);
        this.ctx.lineTo(this.canvas.width, cy);
        this.ctx.moveTo(cx, 0);
        this.ctx.lineTo(cx, this.canvas.height);
        this.ctx.stroke();

        // Draw Agents
        for (const agent of agents) {
            const screenX = cx + (agent.x * 20); // Scale factor
            const screenY = cy - (agent.y * 20);

            this.ctx.fillStyle = agent.battery > 0.2 ? '#00ffaa' : '#ff3333';
            this.ctx.beginPath();
            this.ctx.arc(screenX, screenY, 4, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
}
