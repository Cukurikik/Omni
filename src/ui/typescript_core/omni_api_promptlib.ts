export interface FewShotExample {
    input: string;
    output: string;
}

export class OmniPromptLibAPI {
    /** OMNI Interface Layer: PromptLib API */
    public static compileExample(ex: FewShotExample): string {
        return `Q: ${ex.input}\nA: ${ex.output}`;
    }
}
