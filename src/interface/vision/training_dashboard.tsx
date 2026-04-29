import React from 'react';

interface TrainingMetrics {
    epoch: number;
    loss: number;
    accuracy: number;
    valLoss: number;
    valAccuracy: number;
    learningRate: number;
    timeRemainingMs: number;
}

interface TrainingDashboardProps {
    metrics: TrainingMetrics | null;
    history: { epoch: number, loss: number, valLoss: number }[];
    status: 'idle' | 'training' | 'completed' | 'error';
}

export const OmniTrainingDashboard: React.FC<TrainingDashboardProps> = ({ metrics, history, status }) => {
    
    const formatTime = (ms: number) => {
        const totalSeconds = Math.floor(ms / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    return (
        <div className="omni-training-dashboard bg-slate-900 p-6 rounded-xl border border-slate-700 text-slate-200 shadow-2xl max-w-5xl mx-auto">
            <header className="flex justify-between items-center mb-8 border-b border-slate-700 pb-4">
                <div>
                    <h1 className="text-2xl font-bold text-sky-400">Vision Model Training</h1>
                    <p className="text-sm text-slate-400 font-mono mt-1">ResNet-50 / Omni-ImgClsMob</p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="relative flex h-3 w-3">
                        {status === 'training' && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>}
                        <span className={`relative inline-flex rounded-full h-3 w-3 ${
                            status === 'training' ? 'bg-emerald-500' : 
                            status === 'error' ? 'bg-red-500' : 
                            status === 'completed' ? 'bg-sky-500' : 'bg-slate-500'
                        }`}></span>
                    </span>
                    <span className="text-sm font-semibold uppercase tracking-wider text-slate-300">
                        {status}
                    </span>
                </div>
            </header>

            {metrics ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                    <MetricCard title="Epoch" value={metrics.epoch.toString()} />
                    <MetricCard title="Training Loss" value={metrics.loss.toFixed(4)} color="text-rose-400" />
                    <MetricCard title="Training Acc" value={`${(metrics.accuracy * 100).toFixed(2)}%`} color="text-emerald-400" />
                    <MetricCard title="Validation Loss" value={metrics.valLoss.toFixed(4)} color="text-rose-400" />
                    <MetricCard title="Validation Acc" value={`${(metrics.valAccuracy * 100).toFixed(2)}%`} color="text-emerald-400" />
                    <MetricCard title="ETA" value={formatTime(metrics.timeRemainingMs)} color="text-sky-400 font-mono" />
                </div>
            ) : (
                <div className="h-32 flex items-center justify-center border border-dashed border-slate-700 rounded-lg mb-8 text-slate-500">
                    No metrics available
                </div>
            )}

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 h-64 relative">
                <h3 className="text-sm text-slate-400 absolute top-4 left-4">Loss History</h3>
                {/* Simplified SVG Chart Rendering for structural completeness */}
                {history.length > 0 ? (
                    <svg className="w-full h-full mt-4" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <polyline
                            points={history.map((h, i) => `${(i / (history.length - 1 || 1)) * 100},${100 - Math.min(100, h.loss * 20)}`).join(' ')}
                            fill="none"
                            stroke="#f43f5e"
                            strokeWidth="1.5"
                            vectorEffect="non-scaling-stroke"
                        />
                        <polyline
                            points={history.map((h, i) => `${(i / (history.length - 1 || 1)) * 100},${100 - Math.min(100, h.valLoss * 20)}`).join(' ')}
                            fill="none"
                            stroke="#3b82f6"
                            strokeWidth="1.5"
                            vectorEffect="non-scaling-stroke"
                        />
                    </svg>
                ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-600 text-sm">Waiting for history...</div>
                )}
            </div>
        </div>
    );
};

const MetricCard: React.FC<{ title: string, value: string | number, color?: string }> = ({ title, value, color = "text-white" }) => (
    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex flex-col justify-center">
        <span className="text-xs text-slate-400 uppercase tracking-wide mb-1">{title}</span>
        <span className={`text-2xl font-bold ${color}`}>{value}</span>
    </div>
);
