// OMNI UI Layer - CoML IDE Plugin
import { JSX } from "@omni-bridge/ui/jsx";

type CoMLState = {
    codeSuggestion: string;
    isAnalyzing: boolean;
};

type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function SuggestionPanel(props: { state: CoMLState }): JSX.Element {
    
    const validateSuggestion = (code: string): Result<string, string> => {
        if (!code) return { ok: false, error: "No suggestion available" };
        if (code.length > 5000) return { ok: false, error: "Suggestion too long" };
        return { ok: true, value: code };
    };

    const sug = validateSuggestion(props.state.codeSuggestion);

    return (
        <div className="coml-panel">
            <h3>CoML ML Assistant</h3>
            {props.state.isAnalyzing ? (
                <div className="loader">Analyzing context...</div>
            ) : (
                <div className={`suggestion ${sug.ok ? 'valid' : 'error'}`}>
                    {sug.ok ? <pre><code>{sug.value}</code></pre> : <span>{sug.error}</span>}
                </div>
            )}
        </div>
    );
}
