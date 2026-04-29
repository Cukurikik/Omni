export interface HackGPTConfig {
    theme: string;
    showSystemPrompt: boolean;
}

export class OmniHackGPTAPI {
    /** OMNI Interface Layer: HackGPT API */
    public static initializeTerminal(config: HackGPTConfig): string {
        return `INIT TERM [Theme=${config.theme}] [SysPrompt=${config.showSystemPrompt}]`;
    }
}
