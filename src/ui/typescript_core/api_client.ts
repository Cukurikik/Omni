import { OmniResult } from "../core/result";

export async function callLLMAPI(prompt: string): Promise<OmniResult<string>> {
    try {
        const res = await fetch("/api/v1/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        return { success: true, data: data.text };
    } catch(err) {
        return { success: false, error: String(err) };
    }
}
