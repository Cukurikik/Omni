import React, { useState } from 'react';

export interface OmniResult<T> {
  value: T | null;
  error: string | null;
  isOk: boolean;
}

export const RagChatUI: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);

  const handleSend = (text: string) => {
    const res: OmniResult<string> = {
      value: `User: ${text}`,
      error: null,
      isOk: true
    };
    
    if (res.isOk && res.value) {
      setMessages([...messages, res.value]);
    }
  };

  return (
    <div className="rag-chat">
      <div className="chat-history">
        {messages.map((msg, i) => <div key={i}>{msg}</div>)}
      </div>
      <button onClick={() => handleSend("Test Message")}>Send</button>
    </div>
  );
};
