export interface ExtractedEntity {
    entity: string;
    type: string;
    position: number;
}

export class OmniChatGPTIEAPI {
    /** OMNI Interface Layer: ChatGPT IE API */
    public static filterByType(entities: ExtractedEntity[], targetType: string): ExtractedEntity[] {
        if (!targetType) return entities;
        return entities.filter(e => e.type === targetType);
    }

    public static serializeGraph(entities: ExtractedEntity[]): string {
        return entities.map(e => `[${e.position}] ${e.entity} (${e.type})`).join(' -> ');
    }
}
