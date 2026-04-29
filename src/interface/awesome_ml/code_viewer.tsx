import React from 'react';

interface CodeSnippet {
    file: string;
    score: number;
    embedding: number[];
}

export const CodeEmbeddingsViewer = ({ snippets }: { snippets: CodeSnippet[] }) => {
    return (
        <div className="code-viewer" style={{ padding: '20px', background: '#222', color: '#fff' }}>
            <h2>Source Code Embeddings</h2>
            <ul>
                {snippets.map((s, idx) => (
                    <li key={idx} style={{ marginBottom: '10px', borderBottom: '1px solid #444' }}>
                        <h4>{s.file}</h4>
                        <p>Similarity Score: {s.score.toFixed(3)}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};
