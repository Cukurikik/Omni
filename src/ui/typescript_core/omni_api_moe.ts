export interface ExpertConfig {
    name: string;
    capacity: number;
    domain: string;
}

export class OmniMoEAPI {
    /** OMNI Interface Layer: MoE Configuration API */
    public static validateConfig(experts: ExpertConfig[]): boolean {
        if (experts.length === 0) return false;
        const names = new Set(experts.map(e => e.name));
        if (names.size !== experts.length) return false; // Duplicate names
        return experts.every(e => e.capacity > 0 && e.domain.length > 0);
    }

    public static aggregateLoads(loads: Record<string, number>): number {
        return Object.values(loads).reduce((a, b) => a + b, 0);
    }
}
