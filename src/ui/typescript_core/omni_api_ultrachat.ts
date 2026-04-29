export interface ChatTurn {
    persona: string;
    content: string;
}

export class OmniUltraChatAPI {
    /** OMNI Interface Layer: UltraChat API */
    public static logTurn(turn: ChatTurn): string {
        return `[${turn.persona.toUpperCase()}]: ${turn.content}`;
    }
}
