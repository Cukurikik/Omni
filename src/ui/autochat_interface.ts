// OMNI UI Layer - AutoChat Interface
import { JSX } from "@omni-bridge/ui/jsx";

type Message = { role: "user" | "assistant", content: string };
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

export function ChatBox(props: { messages: Message[] }): JSX.Element {
    
    const renderMessage = (msg: Message): Result<JSX.Element, string> => {
        if (!msg.content) return { ok: false, error: "Empty content" };
        return { 
            ok: true, 
            value: <div className={`msg-${msg.role}`}>{msg.content}</div> 
        };
    };

    return (
        <div className="chat-container">
            {props.messages.map((m, idx) => {
                const res = renderMessage(m);
                return res.ok ? <div key={idx}>{res.value}</div> : <span className="err">Error loading message</span>;
            })}
        </div>
    );
}
