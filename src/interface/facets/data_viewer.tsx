import React from 'react';

interface DatasetStats {
    featureName: string;
    missingCount: number;
    mean: number;
}

export const FacetsDataViewer = ({ stats }: { stats: DatasetStats[] }) => {
    return (
        <div className="facets-viewer">
            <h2>Dataset Overview</h2>
            <table>
                <thead><tr><th>Feature</th><th>Missing</th><th>Mean</th></tr></thead>
                <tbody>
                    {stats.map(s => (
                        <tr key={s.featureName}>
                            <td>{s.featureName}</td>
                            <td>{s.missingCount}</td>
                            <td>{s.mean.toFixed(2)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
