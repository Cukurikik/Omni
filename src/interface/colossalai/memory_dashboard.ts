export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class MemoryDashboard {
    public updateUsage(usedMB: number, totalMB: number): OmniResult<boolean> {
        if (totalMB <= 0 || usedMB < 0) {
            return { value: false, error: "Invalid memory values", isOk: false };
        }

        // TypeScript UI logic for Colossal-AI memory usage dashboard
        const percentage = (usedMB / totalMB) * 100;
        console.log(`Memory Usage: ${percentage.toFixed(1)}%`);
        
        return { value: true, error: null, isOk: true };
    }
}
