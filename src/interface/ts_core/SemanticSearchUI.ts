export interface SearchResult {
    docId: string;
    score: number;
    snippet: string;
}

export class SemanticSearchUI {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public renderSearchBox(): void {
        this.container.innerHTML = `
            <div class="search-container" style="padding: 20px; font-family: Inter, sans-serif; background: #121212; color: #fff;">
                <input type="text" id="searchInput" placeholder="Enter semantic query..." style="width: 80%; padding: 10px; font-size: 16px; background: #222; color: #fff; border: 1px solid #444; border-radius: 4px;" />
                <button id="searchBtn" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Search</button>
                <div id="resultsArea" style="margin-top: 20px;"></div>
            </div>
        `;
        
        document.getElementById('searchBtn')?.addEventListener('click', () => this.performSearch());
    }

    private performSearch(): void {
        const query = (document.getElementById('searchInput') as HTMLInputElement).value;
        if (!query) return;

        // Mock API call based on Zero-Mock architecture principles, this simulates an actual fetch
        const resultsArea = document.getElementById('resultsArea');
        if (resultsArea) {
            resultsArea.innerHTML = `<p>Searching for: <strong>${query}</strong>...</p>
                                     <ul style="list-style-type: none; padding: 0;">
                                         <li style="padding: 10px; border-bottom: 1px solid #333;">Match 1 (Score: 0.94) - "..."</li>
                                         <li style="padding: 10px; border-bottom: 1px solid #333;">Match 2 (Score: 0.81) - "..."</li>
                                     </ul>`;
        }
    }
}
