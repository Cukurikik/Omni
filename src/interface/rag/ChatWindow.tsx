//=============================================================================
// OMNI INTERFACE LAYER — RAG CHAT WINDOW (TYPESCRIPT / REACT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Strongly typed React Component for RAG System interaction.
//=============================================================================

import React, { useState } from 'react';
import { RAGQueryInput, RAGResponse } from '@omni-bridge/domain/rag';
import { NetworkClient } from '@omni-bridge/network';

interface ChatWindowProps {
    sessionId: string;
    theme?: 'light' | 'dark';
}

interface Message {
    id: string;
    role: 'user' | 'ai';
    content: string;
    sources?: Array<{ id: string, source: string }>;
}

/**
 * @html_template("rag-chat")
 */
export const ChatWindow: React.FC<ChatWindowProps> = ({ sessionId, theme = 'dark' }) => {
    const [messages, setMessages] = useState<ts::Array<Message>>([]);
    const [input, setInput] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        // OMNI IDIOM: Monadic error handling in TS via Result object
        const query: RAGQueryInput = { queryText: input, topK: 3 };
        const result = await NetworkClient.graphqlQuery<RAGResponse>('askRAG', query);

        if (result.isOk()) {
            const data = result.unwrap();
            const aiMsg: Message = {
                id: Date.now().toString(),
                role: 'ai',
                content: data.answer,
                sources: data.sources.map(s => ({ id: s.id, source: s.metadata.source }))
            };
            setMessages(prev => [...prev, aiMsg]);
        } else {
            const errorMsg: Message = {
                id: Date.now().toString(),
                role: 'ai',
                content: `Error: ${result.getError().message}`
            };
            setMessages(prev => [...prev, errorMsg]);
        }
        setIsLoading(false);
    };

    return (
        <div className={`omni-chat-container ${theme}`}>
            <div className="omni-chat-history">
                {messages.map(msg => (
                    <div key={msg.id} className={`message ${msg.role}`}>
                        <p>{msg.content}</p>
                        {msg.sources && msg.sources.length > 0 && (
                            <div className="sources">
                                <span>Sources: {msg.sources.map(s => s.source).join(', ')}</span>
                            </div>
                        )}
                    </div>
                ))}
                {isLoading && <div className="loading-indicator">Mother is thinking...</div>}
            </div>
            <div className="omni-chat-input">
                <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask OMNI..."
                />
                <button onClick={handleSend} disabled={isLoading}>Send</button>
            </div>
        </div>
    );
};
