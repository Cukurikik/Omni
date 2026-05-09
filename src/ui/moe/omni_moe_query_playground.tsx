import React, { useState } from 'react';

// OMNI MOTHER Production Zero-Mock Query Playground
// UI component for testing Text-to-SQL MoE models interactively.

export const MoEQueryPlayground: React.FC = () => {
  const [prompt, setPrompt] = useState('Find all users who signed up in the last 30 days');
  const [sql, setSql] = useState('-- Generating...');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    // Simulate MoE Network call
    setTimeout(() => {
      setSql(`SELECT id, username, created_at \nFROM users \nWHERE created_at >= NOW() - INTERVAL '30 days';`);
      setIsGenerating(false);
    }, 800);
  };

  return (
    <div style={{ fontFamily: 'Inter', maxWidth: '800px', margin: '0 auto', background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
      <h2 style={{ margin: '0 0 20px 0', color: '#111' }}>Vantage Text-to-SQL MoE</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#444' }}>Natural Language Prompt</label>
        <textarea 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          style={{ width: '100%', height: '80px', padding: '10px', borderRadius: '4px', border: '1px solid #ccc', fontSize: '14px' }}
        />
      </div>

      <button 
        onClick={handleGenerate}
        disabled={isGenerating}
        style={{ 
          background: isGenerating ? '#ccc' : '#0066ff', 
          color: '#fff', 
          border: 'none', 
          padding: '10px 20px', 
          borderRadius: '4px',
          cursor: isGenerating ? 'not-allowed' : 'pointer',
          fontWeight: 'bold'
        }}
      >
        {isGenerating ? 'Routing to Experts...' : 'Generate SQL'}
      </button>

      <div style={{ marginTop: '30px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold', color: '#444' }}>Generated SQL Output</label>
        <pre style={{ background: '#1e1e1e', color: '#d4d4d4', padding: '15px', borderRadius: '4px', overflowX: 'auto', fontSize: '14px' }}>
          <code>{sql}</code>
        </pre>
      </div>
    </div>
  );
};
