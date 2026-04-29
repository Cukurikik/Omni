// Omni API for OneKE Extraction
export interface ExtractionResult {
    entity: string;
    type: string;
    confidence: number;
}

export class OmniOneKEAPI {
    static formatExtractionResponse(rawText: string, extractedItems: ExtractionResult[]): string {
        if (!extractedItems || extractedItems.length === 0) {
            return JSON.stringify({ status: "no_entities", text: rawText });
        }
        
        return JSON.stringify({
            status: "success",
            original_text_length: rawText.length,
            entities_found: extractedItems.length,
            results: extractedItems
        });
    }
}
