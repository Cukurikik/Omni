export interface InstructionFormat {
    role: "user" | "assistant";
    content: string;
}

export class OmniLLaVAAPI {
    /** OMNI Interface Layer: LLaVA API */
    public static formatDialogue(turns: InstructionFormat[]): string {
        return turns.map(t => `${t.role}: ${t.content}`).join('\\n');
    }
}
