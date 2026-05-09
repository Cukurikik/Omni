// moe_kb_tricks_dashboard.tsx — Interface
// Layer: Interface — KB Tricks Dashboard
// Inspired by: kb-tricks (Knowledge base lifecycle management UI)

import React from 'react';

interface KBProps {
    documentId: string;
    title: string;
    state: 'DRAFT' | 'REVIEW_PENDING' | 'PUBLISHED';
    lastUpdated: string;
}

export const KBDashboard: React.FC<{ items: KBProps[] }> = ({ items }) => {
    return (
        <div className="p-8 max-w-4xl mx-auto font-sans">
            <h1 className="text-2xl font-bold border-b pb-4 mb-6">KB Tricks Lifecycle Manager</h1>
            
            <div className="flex flex-col gap-4">
                {items.map((item) => (
                    <div key={item.documentId} className="flex items-center justify-between p-4 border rounded shadow-sm hover:shadow-md transition-shadow">
                        <div>
                            <h3 className="font-semibold text-lg text-gray-800">{item.title}</h3>
                            <span className="text-sm text-gray-500">Updated: {item.lastUpdated}</span>
                        </div>
                        
                        <div className="flex items-center gap-4">
                            <span className={`px-2 py-1 rounded text-xs font-bold ${
                                item.state === 'PUBLISHED' ? 'bg-green-100 text-green-800' :
                                item.state === 'REVIEW_PENDING' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-800'
                            }`}>
                                {item.state}
                            </span>
                            
                            {item.state === 'DRAFT' && (
                                <button className="bg-blue-600 text-white px-3 py-1 rounded text-sm">Submit Review</button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
