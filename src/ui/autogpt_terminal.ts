// OMNI UI Layer - AutoGPT Terminal
import { JSX } from "@omni-bridge/ui/jsx";

type TerminalState = {
    logs: string[];
    isThinking: boolean;
};

export function AutoGPTTerminal(props: { state: TerminalState }): JSX.Element {
    return (
        <div className="terminal-window bg-black text-green-500 font-mono p-4">
            <div className="log-output">
                {props.state.logs.map((log, i) => (
                    <div key={i} className="log-line">> {log}</div>
                ))}
            </div>
            {props.state.isThinking && <div className="cursor animate-pulse">_</div>}
        </div>
    );
}
