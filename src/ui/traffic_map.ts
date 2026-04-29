// OMNI UI Layer - Traffic Map
import { JSX } from "@omni-bridge/ui/jsx";

type TrafficState = {
    intersectionId: string;
    action: string;
};

type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function TrafficMap(props: { state: TrafficState }): JSX.Element {
    
    const validateAction = (action: string): Result<string, string> => {
        if (!action) return { ok: false, error: "Unknown action" };
        return { ok: true, value: action };
    };

    const actionCheck = validateAction(props.state.action);

    return (
        <div className="traffic-map">
            <h2>Intersection: {props.state.intersectionId}</h2>
            <div className={`status-indicator ${actionCheck.ok ? 'active' : 'error'}`}>
                Current Signal: {actionCheck.ok ? actionCheck.value : actionCheck.error}
            </div>
        </div>
    );
}
