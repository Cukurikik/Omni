// OMNI UI Layer - Resource Monitor
import { JSX } from "@omni-bridge/ui/jsx";

type ResourceState = {
    cpuUsage: number;
    ramUsage: number;
    shardStatus: "active" | "inactive" | "error";
};

type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function MonitorDashboard(props: { state: ResourceState }): JSX.Element {
    const { cpuUsage, ramUsage, shardStatus } = props.state;
    
    const validateStatus = (s: string): Result<string, string> => {
        if (s === "error") return { ok: false, error: "Shard malfunction detected" };
        return { ok: true, value: s };
    };

    const statusCheck = validateStatus(shardStatus);

    return (
        <div className="monitor-panel">
            <h1>LLM Resource Efficiency Monitor</h1>
            <div className="metrics">
                <span>CPU: {cpuUsage.toFixed(2)}%</span>
                <span>RAM: {ramUsage.toFixed(2)}GB</span>
            </div>
            <div className={`status ${!statusCheck.ok ? 'alert' : 'normal'}`}>
                {statusCheck.ok ? "System Normal" : statusCheck.error}
            </div>
        </div>
    );
}
