// OMNI UI Layer - Swarm Visualizer
import { JSX } from "@omni-bridge/ui/jsx";

type SwarmState = {
    activeAgent: string;
    connectedAgents: string[];
};

export function SwarmVisualizer(props: { state: SwarmState }): JSX.Element {
    return (
        <div className="swarm-graph">
            <h2>Swarm Topology</h2>
            <div className="agent-nodes">
                {props.state.connectedAgents.map(agent => (
                    <div key={agent} className={`node ${agent === props.state.activeAgent ? 'active' : 'idle'}`}>
                        {agent}
                    </div>
                ))}
            </div>
        </div>
    );
}
