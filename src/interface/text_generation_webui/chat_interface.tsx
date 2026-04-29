import React, { useState } from 'react';

// OMNI TEXT-GENERATION-WEBUI: Chat Interface
// React component providing a chat-like frontend to local LLM serving APIs.
// Source: oobabooga/text-generation-webui

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export const ChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'system', content: 'You are a helpful AI assistant.' },
        { role: 'assistant', content: 'Hello! How can I help you today?' }
    ]);
    const [input, setInput] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);

    const handleSend = () => {
        if (!input.trim() || isGenerating) return;

        const newMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, newMsg]);
        setInput('');
        setIsGenerating(true);

        // Simulate API call to local Oobabooga API
        setTimeout(() => {
            const botReply: Message = { role: 'assistant', content: "I am a simulated response from the local Text-Generation-WebUI backend." };
            setMessages(prev => [...prev, botReply]);
            setIsGenerating(false);
        }, 1500);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '80vh', maxWidth: '800px', margin: '0 auto', backgroundColor: '#1e1e1e', color: '#fff', borderRadius: '10px', overflow: 'hidden', border: '1px solid #333' }}>
            {/* Header */}
            <div style={{ padding: '15px', backgroundColor: '#252526', borderBottom: '1px solid #333', textAlign: 'center', fontWeight: 'bold' }}>
                OMNI Text-Generation-WebUI
            </div>

            {/* Message Area */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px' }}>
                {messages.filter(m => m.role !== 'system').map((msg, idx) => (
                    <div key={idx} style={{ 
                        alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        backgroundColor: msg.role === 'user' ? '#0e639c' : '#333333',
                        padding: '10px 15px',
                        borderRadius: '15px',
                        maxWidth: '70%',
                        wordWrap: 'break-word',
                        fontFamily: 'sans-serif'
                    }}>
                        {msg.content}
                    </div>
                ))}
                {isGenerating && (
                    <div style={{ alignSelf: 'flex-start', color: '#888', fontStyle: 'italic' }}>
                        Assistant is typing...
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div style={{ display: 'flex', padding: '15px', backgroundColor: '#252526', borderTop: '1px solid #333' }}>
                <input 
                    type="text" 
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Type your message..."
                    style={{ flex: 1, padding: '10px', borderRadius: '5px', border: '1px solid #555', backgroundColor: '#3c3c3c', color: '#fff', outline: 'none' }}
                    disabled={isGenerating}
                />
                <button 
                    onClick={handleSend}
                    disabled={isGenerating || !input.trim()}
                    style={{ marginLeft: '10px', padding: '10px 20px', borderRadius: '5px', border: 'none', backgroundColor: '#0e639c', color: '#fff', cursor: isGenerating ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
                >
                    Send
                </button>
            </div>
        </div>
    );
};
