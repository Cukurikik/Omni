export interface DocumentQuery {
    pdfIds: string[];
    query: string;
}

export class OmniMultiPDFAPI {
    /** OMNI Interface Layer: Multi-PDF Chat API */
    public static buildSearchRequest(q: DocumentQuery): string {
        return `SEARCH_INDEX IN [${q.pdfIds.join(',')}] FOR: "${q.query}"`;
    }

    public static validateIds(pdfIds: string[]): boolean {
        return pdfIds.length > 0 && pdfIds.length <= 10; // Max 10 PDFs at a time
    }
}
