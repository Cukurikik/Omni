export interface DiffusionParams {
    steps: number;
    guidanceScale: number;
}

export class OmniSURAdapterAPI {
    /** OMNI Interface Layer: SUR-Adapter API */
    public static buildPrompt(text: string, params: DiffusionParams): string {
        return `[SUR] Gen: "${text}" | Steps: ${params.steps} | CFG: ${params.guidanceScale}`;
    }
}
