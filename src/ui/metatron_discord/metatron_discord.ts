// OMNI METATRON DISCORD UI
// Event-driven Discord Webhooks UI overlay proxy boundaries.

export type MetatronUIResult<T> = {
    value: T | null;
    error: string;
    is_ok: boolean;
};

export class MetatronDiscordUI {
    private max_message_length: number;
    private image_generation_toggle: boolean;

    constructor(maxLength: number = 2000) {
        this.max_message_length = maxLength;
        this.image_generation_toggle = true;
    }

    public renderChatInterface(messageLength: number, hasImage: boolean): MetatronUIResult<boolean> {
        if (messageLength < 0) {
            return { value: null, error: "NEGATIVE_MESSAGE_LENGTH", is_ok: false };
        }

        if (messageLength > this.max_message_length) {
            return { value: null, error: "DISCORD_MESSAGE_LIMIT_EXCEEDED", is_ok: false };
        }

        if (hasImage && !this.image_generation_toggle) {
            return { value: null, error: "IMAGE_GENERATION_DISABLED_BY_ADMIN", is_ok: false };
        }

        // Return DOM validation pass
        return { value: true, error: "", is_ok: true };
    }
}
