export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class ImpactChartUI {
    public plotSubsetImpacts(impacts: Record<string, number>): OmniResult<boolean> {
        if (!impacts) {
            return { value: false, error: "No impact data", isOk: false };
        }

        // TypeScript UI charting the performance impact of various datablations
        console.log(`Plotting impacts for ${Object.keys(impacts).length} subsets`);
        
        return { value: true, error: null, isOk: true };
    }
}
