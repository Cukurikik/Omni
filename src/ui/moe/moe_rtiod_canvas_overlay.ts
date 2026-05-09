// moe_rtiod_canvas_overlay.ts — Interface Layer: RTIOD Canvas Overlay
// TypeScript class for drawing bounding boxes on video/image streams.

export class BBoxOverlay {
    private ctx: CanvasRenderingContext2D;

    constructor(canvas: HTMLCanvasElement) {
        this.ctx = canvas.getContext('2d')!;
    }

    public clear() {
        this.ctx.clearRect(0, 0, this.ctx.canvas.width, this.ctx.canvas.height);
    }

    public drawBox(x: number, y: number, w: number, h: number, label: string, color: string = 'red') {
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(x, y, w, h);

        // Draw label background
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x, y - 20, this.ctx.measureText(label).width + 10, 20);

        // Draw label text
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '14px Arial';
        this.ctx.fillText(label, x + 5, y - 5);
    }
}
