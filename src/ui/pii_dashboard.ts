// OMNI UI Layer - PII Dashboard
import { JSX } from "@omni-bridge/ui/jsx";

type PIIState = {
    logsScanned: number;
    violationsDetected: number;
};

type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function PIIDashboard(props: { state: PIIState }): JSX.Element {
    
    const calculateRisk = (scanned: number, violations: number): Result<number, string> => {
        if (scanned < 0 || violations < 0) return { ok: false, error: "Invalid metrics" };
        if (scanned === 0) return { ok: true, value: 0 };
        return { ok: true, value: (violations / scanned) * 100 };
    };

    const risk = calculateRisk(props.state.logsScanned, props.state.violationsDetected);

    return (
        <div className="pii-dashboard">
            <h2>GDPR Compliance Monitor</h2>
            {risk.ok ? (
                <div>Risk Level: {risk.value.toFixed(2)}%</div>
            ) : (
                <div className="error">{risk.error}</div>
            )}
        </div>
    );
}
