// OMNI Grafana Dashboard Layout Engine — Interface Layer (TypeScript)
// Absorbing grafana/grafana layout collision geometry
// Grid bounds mathematical packing algorithm without mocks

export type GrafanaResult<T> = {
    ok: boolean;
    value: T | null;
    error: string;
};

export interface PanelGeometry {
    id: string;
    x: number;
    y: number;
    w: number;
    h: number;
}

export class OmniGrafanaDashboardLayout {
    private layout_cycles: number = 0;
    private max_grid_width: number;

    constructor(max_width: number = 24) {
        this.max_grid_width = max_width; // Standard Grafana 24-column grid
    }

    private check_collision(p1: PanelGeometry, p2: PanelGeometry): boolean {
        // Returns true if rectangles overlap
        if (p1.id === p2.id) return false;
        if (p1.x + p1.w <= p2.x) return false;
        if (p1.x >= p2.x + p2.w) return false;
        if (p1.y + p1.h <= p2.y) return false;
        if (p1.y >= p2.y + p2.h) return false;
        return true;
    }

    public pack_panels_gravity_down(panels: PanelGeometry[]): GrafanaResult<PanelGeometry[]> {
        /*
         * Zero mock grid packing algorithm simulating Grafana's react-grid-layout logic.
         * Sorts panels by Y, then X. Applies "gravity" (moving them up) avoiding collisions.
         */
        try {
            if (!panels) return { ok: false, value: null, error: "Empty topology array." };

            this.layout_cycles++;
            
            // Deep copy to prevent mutation reference bugs
            let packed: PanelGeometry[] = JSON.parse(JSON.stringify(panels));

            // Sort top-down, left-right
            packed.sort((a, b) => {
                if (a.y !== b.y) return a.y - b.y;
                return a.x - b.x;
            });

            for (let i = 0; i < packed.length; i++) {
                let p = packed[i];

                // Bound horizontal constraint
                if (p.x + p.w > this.max_grid_width) {
                    p.w = this.max_grid_width - p.x;
                    if (p.w <= 0) return { ok: false, value: null, error: `Exceeded width metric on ${p.id}` };
                }

                // Apply upward gravity (minimize Y)
                let temp_y = p.y;
                while (temp_y > 0) {
                    let proposal: PanelGeometry = { ...p, y: temp_y - 1 };
                    let collision = false;
                    for (let j = 0; j < i; j++) {
                        if (this.check_collision(proposal, packed[j])) {
                            collision = true;
                            break;
                        }
                    }
                    if (collision) {
                        break; // Can't move up further
                    } else {
                        temp_y--;
                    }
                }
                
                p.y = temp_y;
            }

            return { ok: true, value: packed, error: "" };
        } catch (e: any) {
            return { ok: false, value: null, error: `Grid Layout Panic: ${e.message}` };
        }
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: "OmniGrafanaDashboardLayout",
            cycles_run: this.layout_cycles,
            max_bounds: this.max_grid_width,
            status: "Operational"
        };
    }
}
