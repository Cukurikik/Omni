import React from 'react';

// OmniSkeleton.tsx — UI Loading Skeleton
// Layer: Interface / TypeScript
//
// An animated, accessible skeleton placeholder for rendering layouts while
// asynchronous data is being fetched. Strictly matches OMNI design guidelines.

export interface OmniSkeletonProps {
    variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
    width?: string | number;
    height?: string | number;
    className?: string;
    animate?: boolean;
}

export const OmniSkeleton: React.FC<OmniSkeletonProps> = ({
    variant = 'text',
    width,
    height,
    className = '',
    animate = true
}) => {
    
    const baseClasses = "bg-slate-200 dark:bg-slate-700/50";
    const animationClass = animate ? "animate-pulse" : "";
    
    let variantClasses = "";
    let defaultHeight = "";
    
    switch (variant) {
        case 'circular':
            variantClasses = "rounded-full";
            break;
        case 'rectangular':
            variantClasses = "rounded-none";
            break;
        case 'rounded':
            variantClasses = "rounded-xl";
            break;
        case 'text':
        default:
            variantClasses = "rounded-md";
            defaultHeight = "h-4"; // Standard text height
            break;
    }

    // Convert numeric dimensions to pixels
    const style: React.CSSProperties = {
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
    };

    return (
        <div 
            className={`
                ${baseClasses} 
                ${animationClass} 
                ${variantClasses} 
                ${!height ? defaultHeight : ''} 
                ${!width && variant === 'text' ? 'w-full' : ''} 
                ${className}
            `}
            style={style}
            aria-hidden="true"
        />
    );
};

// Convenience component for a block of text lines
export const OmniSkeletonTextGroup: React.FC<{ lines?: number; className?: string }> = ({ 
    lines = 3, 
    className = '' 
}) => {
    return (
        <div className={`space-y-3 ${className}`}>
            {Array.from({ length: lines }).map((_, i) => (
                <OmniSkeleton 
                    key={i} 
                    variant="text" 
                    width={i === lines - 1 ? '75%' : '100%'} 
                />
            ))}
        </div>
    );
};
