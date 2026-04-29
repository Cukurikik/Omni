export interface LoRAConfig {
    r: number;
    lora_alpha: number;
    target_modules: string[];
}

export class OmniFastLoRAAPI {
    /** OMNI Interface Layer: FastLoRA API */
    public static validateConfig(config: LoRAConfig): boolean {
        return config.r > 0 && config.lora_alpha > 0 && config.target_modules.length > 0;
    }
}
