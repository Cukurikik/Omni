import { OmniResult } from "../core/result";

export async function fetchBenchmarkMetrics(taskId: string): Promise<OmniResult<any>> {
    const res = await fetch(`/api/bench/${taskId}`);
    if(!res.ok) return {success: false, error: "Fetch failed"};
    return {success: true, data: await res.json()};
}
