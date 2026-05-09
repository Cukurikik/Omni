// moe_chat_navigator_outline.ts — Interface Layer: Chat Navigator Outline
// TS hook maintaining a live outline of heading topics parsed from LLM messages.

import { useState, useEffect } from 'react';

export interface OutlineItem {
    id: string;
    level: number; // 1 for h1, 2 for h2
    text: string;
}

export function useChatOutline() {
    const [outline, setOutline] = useState<OutlineItem[]>([]);

    const updateOutline = (htmlString: string) => {
        // Zero-mock DOM parsing
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlString, 'text/html');
        
        const headings = doc.querySelectorAll('h1, h2, h3');
        const newOutline: OutlineItem[] = [];
        
        headings.forEach((h, index) => {
            const id = `heading-${Date.now()}-${index}`;
            h.id = id; // Inject id for anchor scrolling
            
            newOutline.push({
                id: id,
                level: parseInt(h.tagName.charAt(1)),
                text: h.textContent || 'Untitled Section'
            });
        });
        
        setOutline(prev => [...prev, ...newOutline]);
    };

    const clearOutline = () => setOutline([]);

    return { outline, updateOutline, clearOutline };
}
