// Omni API for RoboPlanner Spatial
export interface SpatialCoordinate {
    x: number;
    y: number;
    z: number;
}

export class OmniRoboPlannerAPI {
    static serializeTrajectory(points: SpatialCoordinate[]): string {
        return JSON.stringify({
            path_points: points.length,
            sequence: points.map(p => [p.x, p.y, p.z])
        });
    }
}
