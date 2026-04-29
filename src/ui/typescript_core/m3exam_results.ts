import { OmniResult } from "../core/result";

export async function loadExamResults(modelId: string): Promise<OmniResult<any>> {
    const res = await fetch(`/api/m3exam/results/${modelId}`);
    if (!res.ok) return {success: false, error: "Failed load"};
    return {success: true, data: await res.json()};
}
