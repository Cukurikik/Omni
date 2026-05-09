import React, { useState } from 'react';

// OmniDataTable.tsx — Reusable Data Table
// Layer: Interface / TypeScript
//
// A robust, accessible React data table component. Implements client-side 
// pagination, sorting, and strictly adheres to OMNI styling. Zero mock.

export interface ColumnDef<T> {
    key: keyof T | string;
    header: string;
    render?: (row: T) => React.ReactNode;
    sortable?: boolean;
}

export interface OmniDataTableProps<T> {
    data: T[];
    columns: ColumnDef<T>[];
    rowsPerPage?: number;
    className?: string;
}

export function OmniDataTable<T extends { id: string | number }>({
    data,
    columns,
    rowsPerPage = 10,
    className = ''
}: OmniDataTableProps<T>) {
    
    const [currentPage, setCurrentPage] = useState(1);
    const [sortKey, setSortKey] = useState<string | null>(null);
    const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

    // Sorting Logic
    const sortedData = React.useMemo(() => {
        if (!sortKey) return data;
        
        return [...data].sort((a, b) => {
            const valA = (a as any)[sortKey];
            const valB = (b as any)[sortKey];
            
            if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
            if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    }, [data, sortKey, sortDirection]);

    // Pagination Logic
    const totalPages = Math.ceil(sortedData.length / rowsPerPage);
    const paginatedData = sortedData.slice(
        (currentPage - 1) * rowsPerPage, 
        currentPage * rowsPerPage
    );

    const handleSort = (key: string) => {
        if (sortKey === key) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortKey(key);
            setSortDirection('asc');
        }
    };

    return (
        <div className={`bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden ${className}`}>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
                            {columns.map((col) => (
                                <th 
                                    key={String(col.key)}
                                    onClick={() => col.sortable && handleSort(String(col.key))}
                                    className={`px-6 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider ${col.sortable ? 'cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-700' : ''}`}
                                >
                                    <div className="flex items-center">
                                        {col.header}
                                        {sortKey === String(col.key) && (
                                            <span className="ml-1">
                                                {sortDirection === 'asc' ? '↑' : '↓'}
                                            </span>
                                        )}
                                    </div>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-700/50">
                        {paginatedData.map((row) => (
                            <tr key={row.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/20 transition-colors">
                                {columns.map((col) => (
                                    <td key={String(col.key)} className="px-6 py-4 text-sm text-slate-700 dark:text-slate-300">
                                        {col.render ? col.render(row) : String((row as any)[col.key])}
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            
            {/* Pagination Controls */}
            {totalPages > 1 && (
                <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50">
                    <span className="text-sm text-slate-500 dark:text-slate-400">
                        Page {currentPage} of {totalPages}
                    </span>
                    <div className="flex space-x-2">
                        <button 
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="px-3 py-1 text-sm border border-slate-200 dark:border-slate-600 rounded-md disabled:opacity-50 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-700"
                        >
                            Previous
                        </button>
                        <button 
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="px-3 py-1 text-sm border border-slate-200 dark:border-slate-600 rounded-md disabled:opacity-50 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-700"
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
