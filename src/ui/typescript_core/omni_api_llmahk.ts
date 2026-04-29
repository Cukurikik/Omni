export interface AHKTrigger {
    hotkey: string;
    promptTemplate: string;
}

export class OmniLLMAHKAPI {
    /** OMNI Interface Layer: LLM AHK API */
    public static bindKey(trigger: AHKTrigger): string {
        return `Bound ${trigger.hotkey} to prompt trigger.`;
    }
}
