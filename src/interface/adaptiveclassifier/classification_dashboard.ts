export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class ClassificationDashboard {
    public updateClassMetrics(className: string, f1Score: number): OmniResult<boolean> {
        if (!className || f1Score < 0 || f1Score > 1) {
            return { value: false, error: "Invalid metrics", isOk: false };
        }

        // TypeScript UI reactivity integration
        console.log(`Updating dashboard for class ${className} with F1: ${f1Score}`);
        
        return { value: true, error: null, isOk: true };
    }
}
