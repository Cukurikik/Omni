export interface Result<T> {
    value?: T;
    error?: string;
}

export function renderDashboard(metrics: any): Result<string> {
    if (!metrics) return { error: "No metrics" };
    return { value: "<div>Dashboard</div>" };
}
