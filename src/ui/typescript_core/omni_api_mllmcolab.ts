export interface SessionConfig {
    modelId: string;
    precision: 'fp16' | 'fp32' | 'int8';
}

export class OmniMLLMColabAPI {
    /** OMNI Interface Layer: MLLM Colab API */
    public static generateLaunchCommand(config: SessionConfig): string {
        return `python launch.py --model ${config.modelId} --dtype ${config.precision}`;
    }
}
