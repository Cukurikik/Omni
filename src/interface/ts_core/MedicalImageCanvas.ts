export class MedicalImageCanvas {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;

    constructor(canvasId: string) {
        const el = document.getElementById(canvasId) as HTMLCanvasElement;
        if (!el) throw new Error(`Canvas ${canvasId} not found`);
        this.canvas = el;
        this.ctx = el.getContext('2d')!;
    }

    public drawSegmentationOverlay(maskData: Uint8ClampedArray, width: number, height: number): void {
        const imageData = new ImageData(maskData, width, height);
        this.ctx.putImageData(imageData, 0, 0);
    }
}
