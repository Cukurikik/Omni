import React from 'react';

interface Document {
    id: number;
    title: string;
    created: string;
    tags: string[];
    thumbnailUrl: string;
}

export const DocumentGrid = ({ documents }: { documents: Document[] }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
            {documents.map(doc => (
                <div key={doc.id} className="border rounded shadow-sm bg-white overflow-hidden hover:shadow-md transition">
                    <img src={doc.thumbnailUrl} alt={doc.title} className="w-full h-48 object-cover border-b" />
                    <div className="p-3">
                        <h3 className="font-bold text-gray-800 truncate">{doc.title}</h3>
                        <p className="text-xs text-gray-500 mt-1">{new Date(doc.created).toLocaleDateString()}</p>
                        <div className="mt-2 flex flex-wrap gap-1">
                            {doc.tags.map(tag => (
                                <span key={tag} className="bg-blue-100 text-blue-800 text-[10px] px-2 py-0.5 rounded-full">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};
