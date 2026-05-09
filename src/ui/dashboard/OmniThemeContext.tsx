import React, { createContext, useContext, useState, ReactNode } from 'react';

// OmniThemeContext.tsx — UI Theme Management
// Layer: Interface / TypeScript
//
// Strictly typed React Context for managing application-wide theming,
// dark mode toggling, and CSS variable injection for the OMNI Dashboard.

export type ThemeType = 'light' | 'dark' | 'system';

interface OmniThemeState {
    theme: ThemeType;
    setTheme: (theme: ThemeType) => void;
    resolvedTheme: 'light' | 'dark'; // What is actually being displayed
}

const OmniThemeContext = createContext<OmniThemeState | undefined>(undefined);

interface OmniThemeProviderProps {
    children: ReactNode;
    defaultTheme?: ThemeType;
}

export const OmniThemeProvider: React.FC<OmniThemeProviderProps> = ({ 
    children, 
    defaultTheme = 'system' 
}) => {
    const [theme, setTheme] = useState<ThemeType>(defaultTheme);

    // Determine actual rendered theme
    const getResolvedTheme = (): 'light' | 'dark' => {
        if (theme !== 'system') return theme;
        if (typeof window === 'undefined') return 'dark'; // Default SSR
        
        return window.matchMedia('(prefers-color-scheme: dark)').matches 
            ? 'dark' 
            : 'light';
    };

    const resolvedTheme = getResolvedTheme();

    // Effect to apply theme to document root for global CSS variable styling
    React.useEffect(() => {
        const root = document.documentElement;
        
        root.classList.remove('light', 'dark');
        root.classList.add(resolvedTheme);
        
        // Example dynamic CSS variable injection
        if (resolvedTheme === 'dark') {
            root.style.setProperty('--omni-bg-primary', '#0f172a');
            root.style.setProperty('--omni-text-primary', '#f8fafc');
        } else {
            root.style.setProperty('--omni-bg-primary', '#ffffff');
            root.style.setProperty('--omni-text-primary', '#0f172a');
        }
        
    }, [resolvedTheme]);

    return (
        <OmniThemeContext.Provider value={{ theme, setTheme, resolvedTheme }}>
            {children}
        </OmniThemeContext.Provider>
    );
};

export const useOmniTheme = (): OmniThemeState => {
    const context = useContext(OmniThemeContext);
    if (context === undefined) {
        throw new Error('useOmniTheme must be used within an OmniThemeProvider');
    }
    return context;
};
