export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class HarnessUI {
    public displayResult(output: string): OmniResult<boolean> {
        if (!output) {
            return { value: false, error: "Empty output", isOk: false };
        }
        
        // DOM manipulation logic
        console.log(`Rendered Output: ${output}`);
        return { value: true, error: null, isOk: true };
    }
}
