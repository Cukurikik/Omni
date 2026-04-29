export class OmniAresRobotAPI {
    public static taskScore(distToGoal: number, maxDist: number): number {
        return maxDist > 0 ? 1 - distToGoal / maxDist : 0;
    }
    public static headingError(current: number, target: number): number {
        let e = target - current;
        while (e > Math.PI) e -= 2 * Math.PI;
        while (e < -Math.PI) e += 2 * Math.PI;
        return e;
    }
}
