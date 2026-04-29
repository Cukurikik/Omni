export class OmniResult<T> {
    constructor(public value: T | null, public error: string | null) {
        this.isOk = error === null;
    }
    isOk: boolean;
}

export class SandboxRunner {
    public async executeCode(code: string): Promise<OmniResult<string>> {
        if (!code) {
            return new OmniResult(null, "No code provided for execution");
        }

        try {
            // Simulated secure VM execution logic
            const executionOutput = "Execution Result: SUCCESS";
            return new OmniResult(executionOutput, null);
        } catch (error: any) {
            return new OmniResult(null, `Execution failed: ${error.message}`);
        }
    }
}
