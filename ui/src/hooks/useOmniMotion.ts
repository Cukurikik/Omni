import { useEffect } from 'react';

/**
 * Hook to inject the Omni Cinematic System
 * 1. Attaches mouse coordinates to CSS variables for dynamic glow effects
 * 2. Export View Transition utility for smooth DOM routing
 */
export function useOmniMotion() {
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Find elements acting as magnetic cards
      const magneticTargets = document.querySelectorAll('.omni-magnetic');
      
      magneticTargets.forEach((el) => {
        const rect = (el as HTMLElement).getBoundingClientRect();
        
        // Calculate mouse position relative to the element
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Push raw coordinates to CSS context
        (el as HTMLElement).style.setProperty('--mouse-x', `${x}px`);
        (el as HTMLElement).style.setProperty('--mouse-y', `${y}px`);
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);
}

/**
 * Triggers a DOM transition natively (no extra libraries needed).
 * Wraps your state update inside the flushSync/startViewTransition API.
 */
export function transitionDOM(updateCallback: () => void) {
  // Graceful fallback for older browsers or Safari without View Transitions
  if (!document.startViewTransition) {
    updateCallback();
    return;
  }
  
  // High-performance Cinematic DOM Swap
  document.startViewTransition(() => {
    updateCallback();
  });
}
