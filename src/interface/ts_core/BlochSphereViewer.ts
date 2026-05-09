export class BlochSphereViewer {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public renderState(theta: number, phi: number): void {
        // Zero-mock 2D projection of a 3D Bloch sphere
        
        const cx = 150;
        const cy = 150;
        const radius = 100;
        
        // Spherical to Cartesian
        const x = radius * Math.sin(theta) * Math.cos(phi);
        const y = radius * Math.cos(theta); // Z in Bloch sphere maps to Y on canvas
        
        this.container.innerHTML = `
            <div style="background: #ffffff; border: 2px solid #ccc; width: 300px; height: 300px; position: relative; border-radius: 5px;">
                <svg width="300" height="300">
                    <!-- Sphere outline -->
                    <circle cx="${cx}" cy="${cy}" r="${radius}" stroke="#000" stroke-width="1" fill="none" />
                    <!-- Equator -->
                    <ellipse cx="${cx}" cy="${cy}" rx="${radius}" ry="${radius/3}" stroke="#ccc" stroke-dasharray="5,5" fill="none" />
                    <!-- Z axis -->
                    <line x1="${cx}" y1="${cy - radius}" x2="${cx}" y2="${cy + radius}" stroke="#ccc" stroke-width="1" />
                    <!-- State vector -->
                    <line x1="${cx}" y1="${cy}" x2="${cx + x}" y2="${cy - y}" stroke="#ff0000" stroke-width="2" />
                    <circle cx="${cx + x}" cy="${cy - y}" r="4" fill="#ff0000" />
                    <!-- Labels -->
                    <text x="${cx - 10}" y="${cy - radius - 10}">|0></text>
                    <text x="${cx - 10}" y="${cy + radius + 20}">|1></text>
                </svg>
            </div>
        `;
    }
}
