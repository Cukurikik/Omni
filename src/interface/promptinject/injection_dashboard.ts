export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class InjectionDashboard {
    public updateVulnerabilityScore(score: number): OmniResult<boolean> {
        if (score < 0 || score > 100) {
            return { value: false, error: "Score must be 0-100", isOk: false };
        }

        // TypeScript UI logic for displaying LLM vulnerability metrics
        console.log(`Vulnerability Score: ${score}%`);
        
        return { value: true, error: null, isOk: true };
    }
}
