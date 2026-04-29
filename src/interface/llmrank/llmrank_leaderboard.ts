import { OmniResult, OmniError } from "@omni-bridge/core";

export interface RankedCandidate {
    id: string;
    btProbability: number;
    rank: number;
}

export class LLMRankLeaderboard {
    private readonly MAX_RANK_DISPLAY = 100;
    
    public generateLeaderboard(candidates: RankedCandidate[]): OmniResult<string, OmniError> {
        if (candidates.length > this.MAX_RANK_DISPLAY) {
             return { ok: false, error: { code: "OMNI_UI_LIMIT", message: "Exceeded max leaderboard display limit" } };
        }
        
        // Ensure sorted
        const sorted = [...candidates].sort((a, b) => b.btProbability - a.btProbability);
        
        let html = `<div class="omni-llmrank-board">`;
        html += `<h2>LLMRank Leaderboard (Bradley-Terry)</h2>`;
        html += `<table><thead><tr><th>Rank</th><th>Candidate ID</th><th>Win Prob</th></tr></thead><tbody>`;
        
        sorted.forEach((c, idx) => {
            if (c.btProbability < 0 || c.btProbability > 1) {
                // Return early on invalid math state
                return { ok: false, error: { code: "OMNI_MATH_ERR", message: "Probability bounds violated" } };
            }
            html += `<tr>
                <td>${idx + 1}</td>
                <td>${c.id}</td>
                <td>${(c.btProbability * 100).toFixed(1)}%</td>
            </tr>`;
        });
        
        html += `</tbody></table></div>`;
        return { ok: true, payload: html };
    }
}
