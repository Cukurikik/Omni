export interface SchemaDefinition {
    schemaName: string;
    fields: string[];
}

export class OmniLangstructAPI {
    /** OMNI Interface Layer: Langstruct API */
    public static generatePrompt(schema: SchemaDefinition): string {
        return `Extract data conforming to ${schema.schemaName}. Required fields: ${schema.fields.join(', ')}. Return valid JSON only.`;
    }
}
