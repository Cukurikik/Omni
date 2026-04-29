export interface DiscordMessage {
    authorId: string;
    content: string;
}

export class OmniChatLLAMAAPI {
    /** OMNI Interface Layer: Chat LLaMA Bot API */
    public static formatResponse(user: string, text: string): string {
        return `<@${user}> ${text}`;
    }
}
