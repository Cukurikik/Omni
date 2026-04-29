// Omni API for Salmonn Audio-Visual Alignment
export interface AudioVisualToken {
    timestamp_ms: number;
    token_id: number;
    modality: 'audio' | 'text' | 'vision';
}

export class OmniSalmonnAPI {
    static serializeMultimodalStream(tokens: AudioVisualToken[]): string {
        // Formats tokens into an interleaving UI-friendly stream
        const sorted = [...tokens].sort((a, b) => a.timestamp_ms - b.timestamp_ms);
        return JSON.stringify({
            stream_length: sorted.length,
            duration_ms: sorted.length > 0 ? sorted[sorted.length - 1].timestamp_ms : 0,
            events: sorted
        });
    }
}
