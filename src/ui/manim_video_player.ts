// OMNI UI Layer - Manim Video Player
import { JSX } from "@omni-bridge/ui/jsx";

type VideoState = {
    url: string;
    status: "rendering" | "ready" | "error";
};

type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function ManimPlayer(props: { state: VideoState }): JSX.Element {
    
    const validateUrl = (url: string): Result<string, string> => {
        if (!url && props.state.status === "ready") return { ok: false, error: "Missing URL for ready video" };
        return { ok: true, value: url };
    };

    const urlCheck = validateUrl(props.state.url);

    return (
        <div className="video-player">
            {props.state.status === "rendering" && <div className="spinner">Generating Animation...</div>}
            {props.state.status === "ready" && urlCheck.ok && (
                <video src={urlCheck.value} controls autoPlay loop />
            )}
            {props.state.status === "error" && <div className="err">Generation Failed</div>}
        </div>
    );
}
