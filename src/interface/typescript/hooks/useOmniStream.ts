import { useState, useEffect } from 'react';

// OMNI MOTHER: React Hook for Server-Sent Events (SSE) (Production Grade)

export function useOmniStream(url: string) {
    const [data, setData] = useState<string>('');
    const [isComplete, setIsComplete] = useState<boolean>(false);

    useEffect(() => {
        const source = new EventSource(url);
        
        source.onmessage = (event) => {
            if (event.data === '[DONE]') {
                setIsComplete(true);
                source.close();
            } else {
                setData(prev => prev + event.data);
            }
        };

        source.onerror = () => {
            console.error('[OMNI STREAM] Error occurred');
            source.close();
        };

        return () => source.close();
    }, [url]);

    return { data, isComplete };
}
