export interface MultimodalPrompt {
    text: string;
    imagePath?: string;
    audioPath?: string;
}

export class OmniXLLMAPI {
    /** OMNI Interface Layer: X-LLM Multimodal API */
    public static hasModalities(prompt: MultimodalPrompt): string[] {
        let mods = ['text'];
        if (prompt.imagePath) mods.push('image');
        if (prompt.audioPath) mods.push('audio');
        return mods;
    }

    public static validatePrompt(prompt: MultimodalPrompt): boolean {
        return prompt.text.length > 0;
    }
}
