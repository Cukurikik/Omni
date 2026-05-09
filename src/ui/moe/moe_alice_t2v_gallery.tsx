// moe_alice_t2v_gallery.tsx — Interface
// Layer: Interface — Alice T2V Gallery Component
// Inspired by: Eric-Alice-T2V-ComfyUI-Wrapper

import React from 'react';

interface VideoResult {
    id: string;
    prompt: string;
    videoUrl: string;
    moeExpertUsed: string;
}

export const AliceGallery: React.FC<{ videos: VideoResult[] }> = ({ videos }) => {
    return (
        <div className="gallery-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            {videos.map((vid) => (
                <div key={vid.id} className="video-card bg-gray-800 rounded-lg overflow-hidden shadow-lg border border-purple-500/30">
                    <video 
                        src={vid.videoUrl} 
                        className="w-full h-48 object-cover" 
                        controls 
                        loop 
                        muted 
                        poster="/assets/loading_poster.png"
                    />
                    <div className="p-4">
                        <p className="text-sm text-gray-300 italic mb-2">"{vid.prompt}"</p>
                        <div className="flex justify-between items-center text-xs">
                            <span className="bg-purple-600 text-white px-2 py-1 rounded">
                                Expert: {vid.moeExpertUsed}
                            </span>
                            <span className="text-gray-500">ID: {vid.id.substring(0, 8)}</span>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
};
