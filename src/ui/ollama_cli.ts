// OMNI UI Layer - Ollama CLI App
import { JSX } from "@omni-bridge/ui/jsx";

type CLIState = {
    modelName: string;
    isDownloading: boolean;
};

export function OllamaCli(props: { state: CLIState }): JSX.Element {
    return (
        <div className="ollama-cli bg-gray-900 text-white font-mono p-4">
            <div>$ ollama run {props.state.modelName}</div>
            {props.state.isDownloading ? (
                <div className="progress-bar">pulling manifest... ⠋</div>
            ) : (
                <div className="prompt">&gt;&gt;&gt; _</div>
            )}
        </div>
    );
}
