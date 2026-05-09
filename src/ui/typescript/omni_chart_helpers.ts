// OMNI MOTHER: Chart configuration helpers for D3/Chart.js

export const OmniChartHelpers = {
    getThemeColors: () => ({
        primary: '#3b82f6',
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        background: '#151b2b',
        gridLines: '#334155'
    }),

    formatLargeNumber: (num: number): string => {
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
        if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
        return num.toString();
    }
};
