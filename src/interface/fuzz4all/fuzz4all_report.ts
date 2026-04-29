import { OmniResult, OmniError } from "@omni-bridge/core";

export interface FuzzMutationReport {
    entropy: number;
    mutationCycles: number;
    crashesFound: number;
}

export class Fuzz4AllReportRenderer {
    private readonly MAX_CRASH_RENDER = 100;
    
    public generateReportHTML(report: FuzzMutationReport): OmniResult<string, OmniError> {
        if (report.entropy < 0) {
            return { ok: false, error: { code: "OMNI_MATH_ERR", message: "Entropy cannot be negative" } };
        }
        
        if (report.crashesFound > this.MAX_CRASH_RENDER) {
            return { ok: false, error: { code: "OMNI_UI_LIMIT", message: "Too many crashes to render safely" } };
        }
        
        const safeHTML = `
            <div class="omni-fuzz-report">
                <h2>Fuzz4All Mutation Analysis</h2>
                <div class="metrics-grid">
                    <div class="metric">
                        <label>Payload Entropy</label>
                        <span>${report.entropy.toFixed(4)} bits</span>
                    </div>
                    <div class="metric">
                        <label>Mutation Cycles</label>
                        <span>${report.mutationCycles}</span>
                    </div>
                    <div class="metric highlight">
                        <label>Crashes Triggered</label>
                        <span>${report.crashesFound}</span>
                    </div>
                </div>
            </div>
        `;
        
        return { ok: true, payload: safeHTML };
    }
}
