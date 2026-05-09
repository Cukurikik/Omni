// moe_youngfly_taigi_bridge.js — Network
// Layer: Network — Youngfly Taigi Open Data API Bridge
// Inspired by: youngfly (Open data for Taigi linguistic dataset)

export class TaigiDataBridge {
    constructor(apiEndpoint) {
        this.apiEndpoint = apiEndpoint || 'https://data.gov.tw/api/v2/taigi';
    }

    async fetchLinguisticCorpus(limit = 1000) {
        try {
            const url = new URL(this.apiEndpoint);
            url.searchParams.append('limit', limit.toString());
            url.searchParams.append('format', 'json');

            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'User-Agent': 'Omni-YoungFly-Bridge/1.0'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return this.transformCorpus(data);
        } catch (error) {
            console.error('[Taigi Bridge] Failed to fetch corpus:', error);
            throw error;
        }
    }

    // Normalizes data structure for OMNI LLM Fine-Tuning
    transformCorpus(rawData) {
        if (!rawData || !rawData.records) return [];
        
        return rawData.records.map(record => ({
            text_zh: record.chinese_translation,
            text_nan: record.taigi_romanization,
            audio_url: record.pronunciation_url || null,
            source: 'YoungFly-MinistryOfEducation'
        }));
    }
}
