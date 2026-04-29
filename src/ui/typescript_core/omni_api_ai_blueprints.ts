export class OmniAIBlueprintsAPI {
    public static criticalPath(durations: number[]): number {
        return durations.length > 0 ? Math.max(...durations) : 0;
    }
}
