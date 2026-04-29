export interface Pose {
    x: number;
    y: number;
    z: number;
}

export class OmniGraspGPTAPI {
    /** OMNI Interface Layer: GraspGPT Controller API */
    public static validatePose(pose: Pose, boundary: number): boolean {
        if (boundary <= 0) return false;
        return Math.abs(pose.x) <= boundary && 
               Math.abs(pose.y) <= boundary && 
               Math.abs(pose.z) <= boundary;
    }

    public static formatCommand(pose: Pose): string {
        return `MOVE_TO X:${pose.x.toFixed(3)} Y:${pose.y.toFixed(3)} Z:${pose.z.toFixed(3)}`;
    }
}
