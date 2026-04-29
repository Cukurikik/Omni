import React from 'react';

export interface OmniResult<T> {
  value: T | null;
  error: string | null;
  isOk: boolean;
}

export const SequenceViewer: React.FC<{ sequenceLength: number }> = ({ sequenceLength }) => {
  const result: OmniResult<boolean> = {
    value: sequenceLength === 8192,
    error: sequenceLength === 8192 ? null : "Suboptimal sequence for Xgen",
    isOk: sequenceLength === 8192
  };

  return (
    <div className="xgen-viewer">
      <h1>Xgen Sequence Viewer</h1>
      <p>Status: {result.isOk ? "Optimized (8k)" : result.error}</p>
    </div>
  );
};
