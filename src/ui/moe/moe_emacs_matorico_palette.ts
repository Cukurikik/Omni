// moe_emacs_matorico_palette.ts — Interface Layer: Emacs Matorico Palette
// TypeScript constants exporting the Matorico Emacs color scheme for web UI usage.

export const MatoricoTheme = {
    colors: {
        background: '#1e1e1e',
        foreground: '#d4d4d4',
        keyword: '#569cd6',
        variable: '#9cdcfe',
        string: '#ce9178',
        comment: '#6A9955',
        function: '#dcdcaa',
        type: '#4ec9b0',
        warning: '#cca700',
        error: '#f44747',
        border: '#444444'
    },
    
    // Injecting as CSS variables into the document
    injectGlobal: function() {
        if (typeof document === 'undefined') return;
        
        const root = document.documentElement;
        Object.entries(this.colors).forEach(([key, value]) => {
            root.style.setProperty(`--matorico-${key}`, value);
        });
    }
};
