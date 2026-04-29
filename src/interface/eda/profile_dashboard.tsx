import React from 'react';

interface ColumnStats {
    dtype: string;
    n_missing: number;
    p_missing: number;
    type?: string;
    mean?: number;
    std?: number;
    min?: number;
    max?: number;
    n_unique?: number;
}

interface ProfileData {
    n_rows: number;
    n_columns: number;
    memory_usage_bytes: number;
    columns: Record<string, ColumnStats>;
}

interface ProfileDashboardProps {
    data: ProfileData | null;
    error: string | null;
}

export const OmniProfileDashboard: React.FC<ProfileDashboardProps> = ({ data, error }) => {
    if (error) {
        return <div className="p-4 bg-red-900/50 text-red-200 rounded border border-red-500">Error: {error}</div>;
    }

    if (!data) {
        return <div className="p-4 text-slate-400">Waiting for profile data...</div>;
    }

    const formatBytes = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className="omni-dashboard p-6 bg-slate-900 text-slate-200 min-h-screen">
            <header className="mb-8 border-b border-slate-700 pb-4">
                <h1 className="text-3xl font-bold text-sky-400 mb-2">Omni Data Profile</h1>
                <div className="flex gap-6 text-sm text-slate-400">
                    <div>Rows: <span className="font-mono text-white">{data.n_rows.toLocaleString()}</span></div>
                    <div>Columns: <span className="font-mono text-white">{data.n_columns.toLocaleString()}</span></div>
                    <div>Memory: <span className="font-mono text-white">{formatBytes(data.memory_usage_bytes)}</span></div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {Object.entries(data.columns).map(([colName, stats]) => (
                    <div key={colName} className="bg-slate-800 rounded-lg p-5 border border-slate-700 shadow-lg">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold truncate pr-2" title={colName}>{colName}</h3>
                            <span className="px-2 py-1 text-xs rounded bg-slate-700 text-slate-300 font-mono">
                                {stats.dtype}
                            </span>
                        </div>
                        
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-slate-400">Missing</span>
                                <span className={stats.p_missing > 0 ? 'text-amber-400' : 'text-slate-200'}>
                                    {(stats.p_missing * 100).toFixed(1)}% ({stats.n_missing})
                                </span>
                            </div>
                            
                            {stats.type === 'numeric' && (
                                <>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Mean</span>
                                        <span className="font-mono">{stats.mean?.toFixed(4)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Min / Max</span>
                                        <span className="font-mono">{stats.min} / {stats.max}</span>
                                    </div>
                                </>
                            )}

                            {stats.type === 'categorical' && (
                                <>
                                    <div className="flex justify-between">
                                        <span className="text-slate-400">Unique</span>
                                        <span className="font-mono">{stats.n_unique}</span>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
