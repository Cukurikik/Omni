export interface BoundingBox3D {
    id: string;
    x: number; y: number; z: number;
    w: number; h: number; d: number;
}

export class OmniVLMGrounderAPI {
    /** OMNI Interface Layer: VLMGrounder API */
    public static getCenter(box: BoundingBox3D) {
        return {
            x: box.x + box.w / 2,
            y: box.y + box.h / 2,
            z: box.z + box.d / 2
        };
    }

    public static serializeBoxes(boxes: BoundingBox3D[]): string {
        return JSON.stringify(boxes);
    }
}
