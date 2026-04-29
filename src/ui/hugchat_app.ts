// OMNI UI Layer - HugChat App
import { JSX } from "@omni-bridge/ui/jsx";

type AppState = {
    messages: { text: string; isBot: boolean }[];
    isConnected: boolean;
};

export function HugChatInterface(props: { state: AppState }): JSX.Element {
    return (
        <div className="hugchat-app">
            <header>
                <h2>HugChat Interface</h2>
                <span className={`status ${props.state.isConnected ? 'online' : 'offline'}`} />
            </header>
            <div className="messages">
                {props.state.messages.map((msg, i) => (
                    <div key={i} className={`msg ${msg.isBot ? 'bot' : 'user'}`}>
                        {msg.text}
                    </div>
                ))}
            </div>
        </div>
    );
}
