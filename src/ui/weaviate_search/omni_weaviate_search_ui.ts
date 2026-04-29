/**
 * OMNI Weaviate Search UI Engine — Interface Layer
 * Absorbing weaviate-tutorials/next-multimodal-search-demo
 * TypeScript UI state controller for multimodal search results rendering.
 */

export interface SearchUiState<T> {
    results: T[];
    query: string;
    loading: boolean;
    error: string | null;
}

interface SearchHit {
    id: string;
    score: number;
    mediaType: 'image' | 'video' | 'audio' | 'text';
    thumbnailUri: string;
    label: string;
}

export class OmniWeaviateSearchUi {
    private renderCycles: number = 0;
    private lastState: SearchUiState<SearchHit> = { results: [], query: '', loading: false, error: null };

    public formatSearchResults(rawHits: any[], query: string): SearchUiState<SearchHit> {
        this.renderCycles++;

        if (!Array.isArray(rawHits)) {
            return { results: [], query, loading: false, error: 'SearchUiError: Invalid hits array' };
        }

        const formatted: SearchHit[] = rawHits.map((hit, idx) => ({
            id: hit.id || `hit-${idx}`,
            score: typeof hit.score === 'number' ? hit.score : 0,
            mediaType: hit.mediaType || 'image',
            thumbnailUri: hit.thumbnail || '',
            label: hit.label || `Result ${idx + 1}`
        }));

        // Sort by score descending
        formatted.sort((a, b) => b.score - a.score);

        this.lastState = { results: formatted, query, loading: false, error: null };
        return this.lastState;
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: 'OmniWeaviateSearchUi',
            renderCycles: this.renderCycles,
            lastResultCount: this.lastState.results.length,
            status: 'Operational'
        };
    }
}
