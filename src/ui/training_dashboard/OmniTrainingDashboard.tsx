// OmniTrainingDashboard.tsx — Training Monitoring Dashboard
// Inspired by: TensorBoard/W&B + OMNI model training
// Layer: Interface / TypeScript React
//
// Real-time training metric visualization with loss curves,
// learning rate schedules, and model comparison views.

import React, { useState, useEffect, useCallback, useMemo } from 'react';

interface MetricPoint {
  step: number;
  value: number;
  timestamp: number;
}

interface TrainingRun {
  runId: string;
  experimentName: string;
  status: 'running' | 'completed' | 'failed' | 'paused';
  startTime: number;
  endTime?: number;
  config: Record<string, string | number | boolean>;
  metrics: Record<string, MetricPoint[]>;
  currentStep: number;
  totalSteps: number;
}

interface DashboardProps {
  runs: TrainingRun[];
  refreshInterval?: number;
  onStopRun?: (runId: string) => void;
  onResumeRun?: (runId: string) => void;
}

interface MetricSummary {
  latest: number;
  best: number;
  mean: number;
  trend: 'improving' | 'degrading' | 'stable';
}

const computeMetricSummary = (points: MetricPoint[], lowerIsBetter: boolean = true): MetricSummary => {
  if (points.length === 0) {
    return { latest: 0, best: 0, mean: 0, trend: 'stable' };
  }

  const values = points.map(p => p.value);
  const latest = values[values.length - 1];
  const best = lowerIsBetter ? Math.min(...values) : Math.max(...values);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;

  // Compute trend from last 10% of points
  const windowSize = Math.max(2, Math.floor(values.length * 0.1));
  const recentValues = values.slice(-windowSize);
  const olderValues = values.slice(-windowSize * 2, -windowSize);

  let trend: 'improving' | 'degrading' | 'stable' = 'stable';
  if (olderValues.length > 0) {
    const recentMean = recentValues.reduce((a, b) => a + b, 0) / recentValues.length;
    const olderMean = olderValues.reduce((a, b) => a + b, 0) / olderValues.length;
    const diff = recentMean - olderMean;
    const threshold = Math.abs(olderMean) * 0.02;

    if (lowerIsBetter) {
      trend = diff < -threshold ? 'improving' : diff > threshold ? 'degrading' : 'stable';
    } else {
      trend = diff > threshold ? 'improving' : diff < -threshold ? 'degrading' : 'stable';
    }
  }

  return { latest, best, mean, trend };
};

const formatDuration = (ms: number): string => {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
};

const formatNumber = (n: number): string => {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  if (Number.isInteger(n)) return n.toString();
  return n.toFixed(4);
};

const StatusBadge: React.FC<{ status: TrainingRun['status'] }> = ({ status }) => {
  const config: Record<string, { color: string; icon: string }> = {
    running: { color: '#4CAF50', icon: '🔄' },
    completed: { color: '#2196F3', icon: '✅' },
    failed: { color: '#f44336', icon: '❌' },
    paused: { color: '#FF9800', icon: '⏸️' },
  };

  const { color, icon } = config[status] || config.paused;

  return (
    <span style={{
      padding: '4px 12px',
      borderRadius: '12px',
      backgroundColor: `${color}22`,
      color: color,
      fontWeight: 600,
      fontSize: '13px',
    }}>
      {icon} {status.toUpperCase()}
    </span>
  );
};

const MetricCard: React.FC<{
  name: string;
  summary: MetricSummary;
  lowerIsBetter?: boolean;
}> = ({ name, summary, lowerIsBetter = true }) => {
  const trendIcon = summary.trend === 'improving' ? '📈' :
                    summary.trend === 'degrading' ? '📉' : '➡️';
  const trendColor = summary.trend === 'improving' ? '#4CAF50' :
                     summary.trend === 'degrading' ? '#f44336' : '#9E9E9E';

  return (
    <div style={{
      padding: '16px',
      borderRadius: '12px',
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      border: '1px solid #2a2a4a',
      minWidth: '180px',
    }}>
      <div style={{ color: '#9E9E9E', fontSize: '12px', marginBottom: '8px' }}>
        {name.toUpperCase()}
      </div>
      <div style={{ color: '#fff', fontSize: '24px', fontWeight: 700 }}>
        {formatNumber(summary.latest)}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
        <span style={{ color: '#64B5F6', fontSize: '12px' }}>
          Best: {formatNumber(summary.best)}
        </span>
        <span style={{ color: trendColor, fontSize: '12px' }}>
          {trendIcon} {summary.trend}
        </span>
      </div>
    </div>
  );
};

const ProgressBar: React.FC<{ current: number; total: number }> = ({ current, total }) => {
  const pct = total > 0 ? (current / total) * 100 : 0;

  return (
    <div style={{ width: '100%', background: '#2a2a4a', borderRadius: '4px', height: '8px' }}>
      <div style={{
        width: `${Math.min(pct, 100)}%`,
        background: 'linear-gradient(90deg, #4CAF50, #8BC34A)',
        borderRadius: '4px',
        height: '100%',
        transition: 'width 0.5s ease',
      }} />
    </div>
  );
};

const RunCard: React.FC<{
  run: TrainingRun;
  onStop?: () => void;
  onResume?: () => void;
}> = ({ run, onStop, onResume }) => {
  const elapsed = (run.endTime || Date.now()) - run.startTime;
  const progress = run.totalSteps > 0 ? (run.currentStep / run.totalSteps) * 100 : 0;
  const eta = progress > 0 ? (elapsed / progress) * (100 - progress) : 0;

  const metricKeys = Object.keys(run.metrics);
  const lossMetrics = metricKeys.filter(k => k.includes('loss'));
  const accuracyMetrics = metricKeys.filter(k => k.includes('acc') || k.includes('f1'));

  return (
    <div style={{
      padding: '20px',
      borderRadius: '16px',
      background: 'linear-gradient(145deg, #0d1117 0%, #161b22 100%)',
      border: '1px solid #30363d',
      marginBottom: '16px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 style={{ color: '#fff', margin: 0 }}>{run.experimentName}</h3>
          <span style={{ color: '#8b949e', fontSize: '13px' }}>ID: {run.runId}</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <StatusBadge status={run.status} />
          {run.status === 'running' && onStop && (
            <button onClick={onStop} style={{
              padding: '6px 16px', borderRadius: '8px', border: '1px solid #f44336',
              background: 'transparent', color: '#f44336', cursor: 'pointer',
            }}>Stop</button>
          )}
          {run.status === 'paused' && onResume && (
            <button onClick={onResume} style={{
              padding: '6px 16px', borderRadius: '8px', border: '1px solid #4CAF50',
              background: 'transparent', color: '#4CAF50', cursor: 'pointer',
            }}>Resume</button>
          )}
        </div>
      </div>

      <div style={{ margin: '16px 0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span style={{ color: '#8b949e', fontSize: '13px' }}>
            Step {formatNumber(run.currentStep)} / {formatNumber(run.totalSteps)}
          </span>
          <span style={{ color: '#8b949e', fontSize: '13px' }}>
            {progress.toFixed(1)}% • ETA: {formatDuration(eta)}
          </span>
        </div>
        <ProgressBar current={run.currentStep} total={run.totalSteps} />
      </div>

      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {lossMetrics.map(key => (
          <MetricCard
            key={key}
            name={key}
            summary={computeMetricSummary(run.metrics[key], true)}
            lowerIsBetter={true}
          />
        ))}
        {accuracyMetrics.map(key => (
          <MetricCard
            key={key}
            name={key}
            summary={computeMetricSummary(run.metrics[key], false)}
            lowerIsBetter={false}
          />
        ))}
      </div>

      <div style={{ marginTop: '12px', color: '#8b949e', fontSize: '12px' }}>
        Elapsed: {formatDuration(elapsed)} •
        LR: {run.config.learning_rate?.toString() || 'N/A'} •
        Batch: {run.config.batch_size?.toString() || 'N/A'}
      </div>
    </div>
  );
};

const OmniTrainingDashboard: React.FC<DashboardProps> = ({
  runs,
  refreshInterval = 5000,
  onStopRun,
  onResumeRun,
}) => {
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('recent');

  const filteredRuns = useMemo(() => {
    let result = [...runs];

    if (filter !== 'all') {
      result = result.filter(r => r.status === filter);
    }

    result.sort((a, b) => {
      if (sortBy === 'recent') return b.startTime - a.startTime;
      if (sortBy === 'progress') return (b.currentStep / b.totalSteps) - (a.currentStep / a.totalSteps);
      return 0;
    });

    return result;
  }, [runs, filter, sortBy]);

  const statusCounts = useMemo(() => ({
    all: runs.length,
    running: runs.filter(r => r.status === 'running').length,
    completed: runs.filter(r => r.status === 'completed').length,
    failed: runs.filter(r => r.status === 'failed').length,
  }), [runs]);

  return (
    <div style={{
      fontFamily: "'Inter', -apple-system, sans-serif",
      background: '#0d1117',
      color: '#c9d1d9',
      minHeight: '100vh',
      padding: '24px',
    }}>
      <h1 style={{ color: '#fff', marginBottom: '24px' }}>
        🧠 OMNI Training Dashboard
      </h1>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
        {Object.entries(statusCounts).map(([key, count]) => (
          <button key={key} onClick={() => setFilter(key)} style={{
            padding: '8px 20px',
            borderRadius: '20px',
            border: filter === key ? '2px solid #58a6ff' : '1px solid #30363d',
            background: filter === key ? '#58a6ff22' : 'transparent',
            color: filter === key ? '#58a6ff' : '#8b949e',
            cursor: 'pointer',
            fontWeight: filter === key ? 600 : 400,
          }}>
            {key.charAt(0).toUpperCase() + key.slice(1)} ({count})
          </button>
        ))}
      </div>

      {filteredRuns.map(run => (
        <RunCard
          key={run.runId}
          run={run}
          onStop={onStopRun ? () => onStopRun(run.runId) : undefined}
          onResume={onResumeRun ? () => onResumeRun(run.runId) : undefined}
        />
      ))}

      {filteredRuns.length === 0 && (
        <div style={{ textAlign: 'center', padding: '48px', color: '#8b949e' }}>
          No training runs match the current filter.
        </div>
      )}
    </div>
  );
};

export default OmniTrainingDashboard;
export { computeMetricSummary, formatDuration, formatNumber };
export type { TrainingRun, MetricPoint, MetricSummary, DashboardProps };
