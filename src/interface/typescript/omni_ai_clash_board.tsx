import React, { useState, useEffect, useRef } from 'react';
import { OmniAiClashArbiter, ClashResult, ArbiterScore } from './omni_ai_clash_arbiter';
import './omni_moebuntu_theme.css'; // Utilizing the Moebuntu kawaii theme

// OMNI MOTHER: AI-Clash React Dashboard (Production Grade)
// Real-time interface for observing the Multi-LLM Clash. Connects via WebSocket.

export const OmniAiClashBoard: React.FC = () => {
    const [prompt, setPrompt] = useState('');
    const [results, setResults] = useState<Record<string, ClashResult>>({});
    const [scores, setScores] = useState<ArbiterScore[]>([]);
    const [isClashing, setIsClashing] = useState(false);
    
    const wsRef = useRef<WebSocket | null>(null);
    const arbiter = new OmniAiClashArbiter("https://api.omni-judge.dev", "sk-mock");

    useEffect(() => {
        // Connect to the Go WebSocket server
        const ws = new WebSocket('ws://localhost:8080/ws');
        
        ws.onopen = () => console.log('[OMNI BOARD] Connected to Clash Hub');
        ws.onmessage = (event) => {
            try {
                const data: ClashResult = JSON.parse(event.data);
                setResults(prev => {
                    const next = { ...prev, [data.modelId]: data };
                    // If we have results from multiple models, run arbiter
                    if (Object.keys(next).length >= 2) {
                        const newScores = arbiter.evaluateHeuristic("Prompt context", Object.values(next));
                        setScores(newScores);
                        setIsClashing(false);
                    }
                    return next;
                });
            } catch (err) {
                console.error('Failed to parse WS message', err);
            }
        };
        
        wsRef.current = ws;
        return () => ws.close();
    }, []);

    const triggerClash = () => {
        if (!prompt || !wsRef.current) return;
        setIsClashing(true);
        setResults({});
        setScores([]);
        
        // Send prompt to server
        wsRef.current.send(JSON.stringify({ action: "trigger", prompt }));
    };

    return (
        <div className="omni-clash-container">
            <header className="omni-header">
                <h1>⚔️ OMNI AI-Clash Arena ⚔️</h1>
                <p>Watch LLMs fight for the best response in real-time.</p>
            </header>

            <div className="omni-input-section">
                <textarea 
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter a complex prompt for the models..."
                    disabled={isClashing}
                />
                <button onClick={triggerClash} disabled={isClashing || !prompt}>
                    {isClashing ? "Models are thinking..." : "INITIATE CLASH"}
                </button>
            </div>

            <div className="omni-results-grid">
                {Object.values(results).map((res) => {
                    const scoreData = scores.find(s => s.modelId === res.modelId);
                    const isWinner = scoreData?.winner;

                    return (
                        <div key={res.modelId} className={`omni-result-card ${isWinner ? 'winner' : ''}`}>
                            <h3>{res.modelId} {isWinner && '👑'}</h3>
                            <div className="metrics">
                                <span className="latency">⏱️ {res.latencyMs}ms</span>
                                {scoreData && <span className="score">⭐ {scoreData.score}/100</span>}
                            </div>
                            <div className="output">
                                {res.output}
                            </div>
                            {scoreData && (
                                <div className="reasoning">
                                    <i>"{scoreData.reasoning}"</i>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
