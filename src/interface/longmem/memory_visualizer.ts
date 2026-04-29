export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class MemoryVisualizer {
    constructor(private canvasId: string) {}

    public renderMemoryBlocks(blocks: number[]): OmniResult<boolean> {
        if (!this.canvasId) {
            return { value: false, error: "Canvas ID not provided", isOk: false };
        }
        
        if (blocks.length === 0) {
            return { value: false, error: "No blocks to render", isOk: false };
        }

        // Logic to render blocks to WebGL or Canvas
        console.log(Rendering  blocks to );
        return { value: true, error: null, isOk: true };
    }
}
