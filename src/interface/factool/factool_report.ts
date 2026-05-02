/**
 * @omni-domain Interface Layer (FacTool)
 * @omni-source various/factool
 * @omni-description FacTool Report mimicking factual verification UI components.
 * @omni-requirement zero-mock, monadic-error
 */

export class OmniResult<T> {
    constructor(public readonly ok: boolean, public readonly value: T | null, public readonly err: Error | null) {}
    static ok<T>(v: T) { return new OmniResult<T>(true, v, null); }
    static err<T>(e: Error) { return new OmniResult<T>(false, null, e); }
}

export interface FactCheckResult {
    claim: string;
    isFactual: boolean;
    confidence: number;
    evidence: string[];
}

export class FacToolReportGenerator {
    public generateHtmlReport(results: FactCheckResult[]): OmniResult<string> {
        if (!results || results.length === 0) {
            return OmniResult.err(new Error("No results provided to generate report"));
        }

        let html = `<div class="factool-report">\n<h2>FacTool Verification Report</h2>\n`;
        
        for (const res of results) {
            const statusClass = res.isFactual ? 'factual' : 'non-factual';
            html += `<div class="claim-card ${statusClass}">\n`;
            html += `  <h3>Claim: ${res.claim}</h3>\n`;
            html += `  <p>Status: <strong>${res.isFactual ? 'Verified' : 'Disputed'}</strong> (Confidence: ${(res.confidence * 100).toFixed(1)}%)</p>\n`;
            if (res.evidence.length > 0) {
                html += `  <ul>\n`;
                res.evidence.forEach(ev => html += `    <li>${ev}</li>\n`);
                html += `  </ul>\n`;
            }
            html += `</div>\n`;
        }
        
        html += `</div>`;
        return OmniResult.ok(html);
    }
}
