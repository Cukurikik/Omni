import { OmniResult } from "../core/result";

export async function submitRAGQuery(query: string): Promise<OmniResult<string[]>> {
    try {
        const res = await fetch("/api/rag/query", {
            method: "POST",
            body: JSON.stringify({ query })
        });
        const data = await res.json();
        return { success: true, data: data.results };
    } catch (e) {
        return { success: false, error: String(e) };
    }
}
