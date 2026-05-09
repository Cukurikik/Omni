export interface EdgeNodeUI {
    id: string;
    x: number;
    y: number;
    status: 'online' | 'training' | 'offline';
}

export class FederatedNetworkMap {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = el;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public renderNetwork(nodes: EdgeNodeUI[]): void {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Background
        this.ctx.fillStyle = '#101020';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Center Aggregator Node
        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        
        // Draw connections
        this.ctx.strokeStyle = '#334466';
        this.ctx.lineWidth = 1;
        for (const n of nodes) {
            if (n.status !== 'offline') {
                this.ctx.beginPath();
                this.ctx.moveTo(cx, cy);
                this.ctx.lineTo(n.x, n.y);
                this.ctx.stroke();
            }
        }

        // Draw Edge Nodes
        for (const n of nodes) {
            this.ctx.fillStyle = n.status === 'training' ? '#ffcc00' : (n.status === 'online' ? '#00ccff' : '#444444');
            this.ctx.beginPath();
            this.ctx.arc(n.x, n.y, 5, 0, Math.PI * 2);
            this.ctx.fill();
        }

        // Draw Aggregator
        this.ctx.fillStyle = '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, 12, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillStyle = '#000';
        this.ctx.font = '10px sans-serif';
        this.ctx.fillText('AG', cx - 7, cy + 3);
    }
}
