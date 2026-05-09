export interface MoleculeNode {
    id: string;
    x: number;
    y: number;
    z: number;
    atomType: string;
}

export class Molecule3DViewer {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public renderMolecule(nodes: MoleculeNode[]): void {
        // Since we cannot import WebGL libraries in Zero-Mock, we output DOM structures
        this.container.innerHTML = `
            <div style="background: #000; width: 100%; height: 400px; position: relative; border: 1px solid #333;">
                <div style="position: absolute; top: 10px; left: 10px; color: #00ffaa; font-family: monospace;">
                    Rendering ${nodes.length} atoms...
                </div>
                ${nodes.map(n => `
                    <div style="
                        position: absolute;
                        left: ${(n.x * 100) + 200}px;
                        top: ${(n.y * 100) + 200}px;
                        width: 10px; height: 10px;
                        background: ${this.getColor(n.atomType)};
                        border-radius: 50%;
                        transform: translate(-50%, -50%);
                        box-shadow: 0 0 5px ${this.getColor(n.atomType)};
                    "></div>
                `).join('')}
            </div>
        `;
    }

    private getColor(atom: string): string {
        switch(atom.toUpperCase()) {
            case 'C': return '#888';
            case 'O': return '#f00';
            case 'N': return '#00f';
            case 'H': return '#fff';
            default: return '#f0f';
        }
    }
}
