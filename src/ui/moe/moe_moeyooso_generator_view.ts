// moe_moeyooso_generator_view.ts — Interface
// Layer: Interface — MoeYooso Random Generator View
// Inspired by: MoeYooso-Random-Generator

export class MoeYoosoView {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found.`);
        this.container = el;
    }

    renderLoading() {
        this.container.innerHTML = `<div class="loading">Summoning Moe Element...</div>`;
    }

    renderResult(data: { trait_name: string, category: string, rarity: string }) {
        // Zero-Mock: Generate DOM nodes safely avoiding innerHTML injections from API
        this.container.innerHTML = '';
        
        const card = document.createElement('div');
        card.className = `moe-card rarity-${data.rarity.toLowerCase()}`;
        
        const title = document.createElement('h2');
        title.textContent = data.trait_name;
        
        const badge = document.createElement('span');
        badge.className = 'category-badge';
        badge.textContent = data.category;

        card.appendChild(title);
        card.appendChild(badge);
        this.container.appendChild(card);
    }
}
