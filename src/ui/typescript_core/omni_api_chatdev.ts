export interface ChatDevRole {
    name: string;
    prompt: string;
}

export class OmniChatDevAPI {
    /** OMNI Interface Layer: ChatDev API */
    public static initializeRole(role: ChatDevRole): string {
        return `You are the ${role.name}. ${role.prompt}`;
    }
}
