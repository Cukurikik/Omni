import { OmniResult } from "../core/result";

export interface TableMetadata {
    rows: number;
    columns: number;
}

export async function fetchTableAnalytics(tableId: string): Promise<OmniResult<TableMetadata>> {
    const res = await fetch(`/api/table/${tableId}`);
    if (!res.ok) {
        return { success: false, error: "Network response was not ok" };
    }
    const data = await res.json();
    return { success: true, data: data };
}
