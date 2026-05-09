export interface DebrisObject {
    id: string;
    x: number;
    y: number;
    dangerLevel: 'low' | 'medium' | 'high';
}

export class OrbitalMapCanvas {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = el;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public renderOrbit(debris: DebrisObject[]): void {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Background Space
        this.ctx.fillStyle = '#050510';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;

        // Draw Earth
        this.ctx.fillStyle = '#1e90ff';
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, 40, 0, Math.PI * 2);
        this.ctx.fill();

        // Draw Debris
        for (const obj of debris) {
            let color = '#00ff00';
            if (obj.dangerLevel === 'medium') color = '#ffff00';
            if (obj.dangerLevel === 'high') color = '#ff0000';

            this.ctx.fillStyle = color;
            this.ctx.beginPath();
            this.ctx.arc(cx + obj.x, cy + obj.y, 2, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Draw velocity tail (mocked)
            this.ctx.strokeStyle = color;
            this.ctx.globalAlpha = 0.5;
            this.ctx.beginPath();
            this.ctx.moveTo(cx + obj.x, cy + obj.y);
            this.ctx.lineTo(cx + obj.x - (obj.y*0.1), cy + obj.y + (obj.x*0.1));
            this.ctx.stroke();
            this.ctx.globalAlpha = 1.0;
        }
    }
}
