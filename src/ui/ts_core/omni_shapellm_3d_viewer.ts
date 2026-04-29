export type ShapeResult<T> = { success: true; data: T } | { success: false; error: string };

export interface Point3D {
    x: number;
    y: number;
    z: number;
}

export class OmniShapeLLMViewer {
    /**
     * WebGL-ready 3D Object Understanding bridge for Embodied Interaction.
     */
    public calculateCentroid(points: Point3D[]): ShapeResult<Point3D> {
        if (!points || points.length === 0) {
            return { success: false, error: "Point cloud cannot be empty" };
        }

        const sum = points.reduce(
            (acc, p) => ({ x: acc.x + p.x, y: acc.y + p.y, z: acc.z + p.z }),
            { x: 0, y: 0, z: 0 }
        );

        return {
            success: true,
            data: {
                x: sum.x / points.length,
                y: sum.y / points.length,
                z: sum.z / points.length,
            }
        };
    }
}
