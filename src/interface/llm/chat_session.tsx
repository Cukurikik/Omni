import React, { useState, useEffect, useRef } from 'react';

// OMNI Strict Types
export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

export interface ChatMessage {
    id: string;
    role: 'system' | 'user' | 'assistant';
    content: string;
    timestamp: number;
}

export interface ChatSessionProps {
    sessionId: string;
    apiEndpoint: string;
}

export const ChatSession: React.FC<ChatSessionProps> = ({ sessionId, apiEndpoint }) => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState<string>('');
    const [isTyping, setIsTyping] = useState<boolean>(false);
    const endOfMessagesRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleInference = async (prompt: string): Promise<MonadicResult<string, string>> => {
        try {
            const res = await fetch(`${apiEndpoint}/infer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, prompt })
            });
            if (!res.ok) {
                return { success: false, error: `HTTP ${res.status}: ${res.statusText}` };
            }
            const data = await res.json();
            if (data.error) {
                return { success: false, error: data.error };
            }
            return { success: true, value: data.result };
        } catch (err: any) {
            return { success: false, error: err.message || 'Network error' };
        }
    };

    const onSend = async () => {
        const trimmed = input.trim();
        if (!trimmed) return;

        const userMsg: ChatMessage = {
            id: crypto.randomUUID(),
            role: 'user',
            content: trimmed,
            timestamp: Date.now()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsTyping(true);

        const result = await handleInference(trimmed);

        if (result.success) {
            const astMsg: ChatMessage = {
                id: crypto.randomUUID(),
                role: 'assistant',
                content: result.value,
                timestamp: Date.now()
            };
            setMessages(prev => [...prev, astMsg]);
        } else {
            const errMsg: ChatMessage = {
                id: crypto.randomUUID(),
                role: 'system',
                content: `Error: ${result.error}`,
                timestamp: Date.now()
            };
            setMessages(prev => [...prev, errMsg]);
        }
        setIsTyping(false);
    };

    return (
        <div className="omni-chat-session">
            <header className="chat-header">
                <h2>OMNI LLM Engine</h2>
                <span className="session-id">Session: {sessionId}</span>
            </header>
            <div className="chat-window">
                {messages.map(msg => (
                    <div key={msg.id} className={`chat-bubble role-${msg.role}`}>
                        <div className="chat-content">{msg.content}</div>
                        <div className="chat-meta">{new Date(msg.timestamp).toLocaleTimeString()}</div>
                    </div>
                ))}
                {isTyping && <div className="chat-bubble typing-indicator">OMNI is processing...</div>}
                <div ref={endOfMessagesRef} />
            </div>
            <div className="chat-input-area">
                <input 
                    type="text" 
                    value={input} 
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && onSend()}
                    disabled={isTyping}
                    placeholder="Enter prompt..."
                />
                <button onClick={onSend} disabled={isTyping || !input.trim()}>
                    Execute
                </button>
            </div>
        </div>
    );
};
