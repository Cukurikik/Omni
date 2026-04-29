export interface ColabGradioOptions {
    share: boolean;
    debug: boolean;
}

export class OmniColabLLMAPI {
    /** OMNI Interface Layer: Use-LLMs-in-Colab API */
    public static launchConfig(opt: ColabGradioOptions): string {
        return `demo.launch(share=${opt.share}, debug=${opt.debug})`;
    }
}
