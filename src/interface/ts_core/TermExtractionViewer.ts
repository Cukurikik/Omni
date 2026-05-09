export interface TermPair {
    source: string;
    target: string;
    score: number;
}

export class TermExtractionViewer {
    private tableContainer: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.tableContainer = el;
    }

    public renderTable(pairs: TermPair[]): void {
        let html = `
            <table style="width: 100%; border-collapse: collapse; font-family: Inter, sans-serif; background: #1e1e1e; color: #fff;">
                <thead>
                    <tr style="background: #333; text-align: left;">
                        <th style="padding: 12px; border-bottom: 2px solid #555;">Source Term</th>
                        <th style="padding: 12px; border-bottom: 2px solid #555;">Target Term</th>
                        <th style="padding: 12px; border-bottom: 2px solid #555;">Alignment Score</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const pair of pairs) {
            const color = pair.score > 0.9 ? '#00ffcc' : (pair.score > 0.7 ? '#ffcc00' : '#ff3366');
            html += `
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #444;">${pair.source}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #444;">${pair.target}</td>
                    <td style="padding: 10px; border-bottom: 1px solid #444; color: ${color};">${(pair.score * 100).toFixed(1)}%</td>
                </tr>
            `;
        }

        html += `</tbody></table>`;
        this.tableContainer.innerHTML = html;
    }
}
