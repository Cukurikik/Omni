export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class WebGLViewport {
    public attachCanvas(canvasId: string): OmniResult<boolean> {
        if (!canvasId) {
            return { value: false, error: "Canvas ID required", isOk: false };
        }

        // TypeScript WebGL/Three.js wrapper for Holodeck generated environments
        console.log(`Attached Holodeck viewport to canvas: ${canvasId}`);
        
        return { value: true, error: null, isOk: true };
    }
}
