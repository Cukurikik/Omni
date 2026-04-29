// OMNI Engine: The Brain Viewer
// TypeScript Engine constraining neuro-symbolic geometry coordinates within canvas bounds.

export class BrainViewerError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "BrainViewerError";
    }
}

export type Result<T> = { value: T; error: null } | { value: null; error: BrainViewerError };

export const Ok = <T>(value: T): Result<T> => ({ value, error: null });
export const Err = (msg: string): Result<any> => ({ value: null, error: new BrainViewerError(msg) });

export class BrainTopologyRenderer {
    private readonly viewportRadiusLimit: number;

    constructor(radiusLimit: number = 4096.0) {
        this.viewportRadiusLimit = radiusLimit;
    }

    public project_3d_to_2d(x: number, y: number, z: number, cameraZ: number): Result<{ screenX: number, screenY: number }> {
        if (cameraZ === 0) {
            return Err("Mathematical singularity: Camera inside manifold space directly");
        }

        const distance = 1.0 / (1.0 - (z / cameraZ));
        
        if (distance <= 0) {
            return Err("Object lies behind projection plane constraints");
        }

        const screenX = x * distance;
        const screenY = y * distance;

        // Bounding
        if (Math.abs(screenX) > this.viewportRadiusLimit || Math.abs(screenY) > this.viewportRadiusLimit) {
            return Err(`Projection vector exceeds renderer limitations (${this.viewportRadiusLimit})`);
        }

        return Ok({ screenX, screenY });
    }

    public calculate_opacity_fade(depthZ: number, maxVisibleDepth: number): Result<number> {
        if (maxVisibleDepth <= 0) return Err("Depth constraint mathematically invalid");
        
        let opacity = 1.0 - (depthZ / maxVisibleDepth);
        opacity = Math.max(0.0, Math.min(1.0, opacity));
        
        return Ok(opacity);
    }
}
