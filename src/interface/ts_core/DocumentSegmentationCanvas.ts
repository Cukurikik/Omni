export interface LayoutBox {
    x: number;
    y: number;
    width: number;
    height: number;
    label: string;
    confidence: number;
}

export class DocumentSegmentationCanvas {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const element = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!element) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = element;
        this.ctx = this.canvas.getContext('2d')!;
    }

    public renderLayout(boxes: LayoutBox[], imageUrl: string): void {
        const img = new Image();
        img.onload = () => {
            this.canvas.width = img.width;
            this.canvas.height = img.height;
            this.ctx.drawImage(img, 0, 0);
            this.drawBoxes(boxes);
        };
        img.src = imageUrl;
    }

    private drawBoxes(boxes: LayoutBox[]): void {
        for (const box of boxes) {
            this.ctx.strokeStyle = this.getColorForLabel(box.label);
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(box.x, box.y, box.width, box.height);
            
            this.ctx.fillStyle = this.ctx.strokeStyle;
            this.ctx.font = '14px sans-serif';
            this.ctx.fillText(`${box.label} (${(box.confidence * 100).toFixed(1)}%)`, box.x, box.y - 5);
        }
    }

    private getColorForLabel(label: string): string {
        const colors: Record<string, string> = {
            'title': '#ff3366',
            'text': '#33ccff',
            'figure': '#33ff33',
            'table': '#ffcc00'
        };
        return colors[label] || '#ffffff';
    }
}
