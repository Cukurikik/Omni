/**
 * OMNI Japanese LLM Explorer — Interface Layer
 * Absorbing llm-jp/awesome-japanese-llm: Japanese LLM overview and comparison UI.
 * TypeScript model registry with benchmarking and comparison state management.
 */

export interface JpLlmModel {
    name: string;
    developer: string;
    parameters: string;
    license: string;
    architecture: string;
    languages: string[];
    benchmarkScores: Record<string, number>;
}

export interface JpLlmResult<T> {
    ok: boolean;
    data?: T;
    error?: string;
}

export class OmniJapaneseLlmExplorer {
    private models: Map<string, JpLlmModel> = new Map();
    private queries: number = 0;

    public registerModel(model: JpLlmModel): JpLlmResult<boolean> {
        if (!model.name) return { ok: false, error: 'JpLlmError: Model name required' };
        this.models.set(model.name, model);
        return { ok: true, data: true };
    }

    public searchModels(filter: { minParams?: number; license?: string; language?: string }): JpLlmResult<JpLlmModel[]> {
        this.queries++;
        let results = Array.from(this.models.values());
        if (filter.license) results = results.filter(m => m.license.toLowerCase().includes(filter.license!.toLowerCase()));
        if (filter.language) results = results.filter(m => m.languages.includes(filter.language!));
        return { ok: true, data: results };
    }

    public compareModels(names: string[], benchmark: string): JpLlmResult<Array<{ name: string; score: number }>> {
        if (names.length < 2) return { ok: false, error: 'JpLlmError: Need at least 2 models to compare' };
        this.queries++;
        const comparison = names.map(n => {
            const m = this.models.get(n);
            return { name: n, score: m?.benchmarkScores[benchmark] || 0 };
        }).sort((a, b) => b.score - a.score);
        return { ok: true, data: comparison };
    }

    public diagnostics(): Record<string, any> {
        return { engine: 'OmniJapaneseLlmExplorer', models: this.models.size,
                 queries: this.queries, status: 'Operational' };
    }
}
