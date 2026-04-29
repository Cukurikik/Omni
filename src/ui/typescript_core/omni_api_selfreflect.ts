export interface ReflectionLog {
    timestamp: number;
    trajectoryHash: string;
    passed: boolean;
}

export class OmniSelfReflectAPI {
    /** OMNI Interface Layer: Self-Reflection API */
    public static filterFailed(logs: ReflectionLog[]): ReflectionLog[] {
        return logs.filter(l => !l.passed);
    }

    public static calculateSuccessRate(logs: ReflectionLog[]): number {
        if (logs.length === 0) return 0;
        const passed = logs.filter(l => l.passed).length;
        return passed / logs.length;
    }
}
