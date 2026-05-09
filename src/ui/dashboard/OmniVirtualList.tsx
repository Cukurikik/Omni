import React, { useState, useEffect, useRef } from 'react';

// OmniVirtualList.tsx — Virtual Scrolling Container
// Layer: Interface / TypeScript
// Inspired by: bvaughn/react-window
//
// Renders only the visible rows of a massive dataset (e.g., 100k+ system logs).
// Drastically reduces the DOM footprint, preventing browser memory crashes 
// and ensuring 60fps scrolling performance. Zero mock.

export interface OmniVirtualListProps<T> {
    items: T[];
    itemHeight: number;
    windowHeight: number;
    renderItem: (item: T, index: number) => React.ReactNode;
    overscanCount?: number;
    className?: string;
}

export function OmniVirtualList<T>({
    items,
    itemHeight,
    windowHeight,
    renderItem,
    overscanCount = 3,
    className = ''
}: OmniVirtualListProps<T>) {
    const [scrollTop, setScrollTop] = useState(0);
    const containerRef = useRef<HTMLDivElement>(null);

    // Calculate total height of the virtual container
    const totalHeight = items.length * itemHeight;

    // Calculate which indices are currently visible
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscanCount);
    const endIndex = Math.min(
        items.length - 1, 
        Math.floor((scrollTop + windowHeight) / itemHeight) + overscanCount
    );

    // Slice only the visible items
    const visibleItems = [];
    for (let i = startIndex; i <= endIndex; i++) {
        visibleItems.push(
            <div 
                key={i}
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: `${itemHeight}px`,
                    transform: `translateY(${i * itemHeight}px)`
                }}
            >
                {renderItem(items[i], i)}
            </div>
        );
    }

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        setScrollTop(e.currentTarget.scrollTop);
    };

    return (
        <div 
            ref={containerRef}
            className={`overflow-y-auto relative ${className}`}
            style={{ height: `${windowHeight}px` }}
            onScroll={handleScroll}
        >
            {/* Inner spacer that forces the container to have the correct scrollbar height */}
            <div style={{ height: `${totalHeight}px`, width: '100%' }}>
                {visibleItems}
            </div>
        </div>
    );
}
