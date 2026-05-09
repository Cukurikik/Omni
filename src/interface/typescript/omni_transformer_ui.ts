// OMNI Interface — Transformer UI Hooks
import { useState, useCallback } from 'react';

export function useOmniInferenceStream(endpoint: string) {
    const [tokens, setTokens] = useState<string>('');
    const [isGenerating, setIsGenerating] = useState<boolean>(false);

    const generate = useCallback(async (prompt: string) => {
        setIsGenerating(true);
        setTokens('');

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                setTokens(prev => prev + chunk);
            }
        } catch (error) {
            console.error("Inference Error:", error);
        } finally {
            setIsGenerating(false);
        }
    }, [endpoint]);

    return { tokens, isGenerating, generate };
}
