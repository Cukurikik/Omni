// OmniLocalChat.tsx — Local LLM Chat UI
// Inspired by: local-chat / Basic-UI-for-GPT-J-6B
// Layer: Interface / TypeScript
//
// React UI component for local language model interaction. Handles streaming
// responses, token counters, and conversation history.

import React, { useState, useRef, useEffect } from 'react';

// Models
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

interface ChatProps {
  apiEndpoint: string;
  modelName: string;
  onTokensUsed?: (count: int) => void;
}

export const OmniLocalChat: React.FC<ChatProps> = ({ apiEndpoint, modelName, onTokensUsed }) => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '0', role: 'system', content: `Connected to Local OMNI Engine: ${modelName}. Ready.`, timestamp: Date.now() }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isTyping) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    const assistantMsgId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '', timestamp: Date.now() }]);

    try {
      const response = await fetch(`${apiEndpoint}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: modelName,
          messages: [...messages, userMsg].filter(m => m.role !== 'system').map(m => ({
            role: m.role,
            content: m.content
          })),
          stream: true
        })
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          
          // Parse SSE (Server-Sent Events)
          const lines = chunk.split('\n').filter(line => line.trim().startsWith('data: '));
          for (const line of lines) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') {
              done = true;
              break;
            }
            try {
              const data = JSON.parse(dataStr);
              if (data.choices && data.choices[0].delta.content) {
                const textChunk = data.choices[0].delta.content;
                setMessages(prev => prev.map(msg => 
                  msg.id === assistantMsgId 
                    ? { ...msg, content: msg.content + textChunk }
                    : msg
                ));
              }
            } catch (e) {
              console.error("Failed to parse SSE JSON", e);
            }
          }
        }
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        role: 'system', 
        content: `Error: ${error instanceof Error ? error.message : "Connection failed."}`, 
        timestamp: Date.now() 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50 border-x border-gray-200 shadow-xl">
      {/* Header */}
      <header className="p-4 bg-slate-900 text-white flex items-center justify-between">
        <h1 className="text-xl font-bold tracking-tight">OMNI Interface</h1>
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-green-400 animate-pulse"></span>
          <span className="text-sm font-mono opacity-80">{modelName}</span>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-none' 
                : msg.role === 'system'
                  ? 'bg-gray-200 text-gray-600 italic text-sm w-full text-center shadow-none'
                  : 'bg-white text-gray-800 rounded-tl-none border border-gray-100'
            }`}>
              <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              {msg.role !== 'system' && (
                <div className={`text-[10px] mt-2 opacity-50 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl rounded-tl-none p-4 shadow-sm border border-gray-100 text-gray-400">
              <span className="animate-pulse">●</span> <span className="animate-pulse delay-100">●</span> <span className="animate-pulse delay-200">●</span>
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </main>

      {/* Input Area */}
      <footer className="p-4 bg-white border-t border-gray-200">
        <form 
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex items-end gap-2"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Send a message to local model..."
            className="flex-1 max-h-32 min-h-[50px] p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={1}
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isTyping}
            className="p-3 bg-blue-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors h-[50px] px-6"
          >
            Send
          </button>
        </form>
        <div className="text-center mt-2 text-xs text-gray-400">
          Powered by OMNI Universal Runtime • Local Execution
        </div>
      </footer>
    </div>
  );
};

export default OmniLocalChat;
