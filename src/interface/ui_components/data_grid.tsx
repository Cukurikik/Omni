import React, { useMemo } from 'react';

export type GridResult<T> = {
    data: T[] | null;
    error: string | null;
};

interface DataGridProps<T> {
    dataset: T[];
    columns: (keyof T)[];
}

export function OmniDataGrid<T extends Record<string, any>>({ dataset, columns }: DataGridProps<T>): React.ReactElement {
    const renderHeaders = useMemo(() => {
        return columns.map(col => <th key={String(col)} className="omni-th">{String(col)}</th>);
    }, [columns]);

    const renderRows = useMemo(() => {
        return dataset.map((row, idx) => (
            <tr key={idx} className="omni-tr">
                {columns.map(col => <td key={String(col)} className="omni-td">{row[col]}</td>)}
            </tr>
        ));
    }, [dataset, columns]);

    return (
        <table className="omni-data-grid" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead><tr>{renderHeaders}</tr></thead>
            <tbody>{renderRows}</tbody>
        </table>
    );
}
