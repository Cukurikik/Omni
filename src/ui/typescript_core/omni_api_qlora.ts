export interface LoRAAdapter {
    rank: number;
    alpha: number;
    targetModules: string[];
}

export class OmniQLoRAAPI {
    /** OMNI Interface Layer: QLoRA API */
    public static calculateScaling(adapter: LoRAAdapter): number {
        if (adapter.rank === 0) return 0.0;
        return adapter.alpha / adapter.rank;
    }

    public static formatInjectionCmd(adapter: LoRAAdapter): string {
        return `INJECT_LORA [R=${adapter.rank}, A=${adapter.alpha}] -> ${adapter.targetModules.join(',')}`;
    }
}
