import React, { useState } from 'react';

// OMNI DIFFUSERS: Generation Gallery
// React TSX UI for browsing generated diffusion images and their associated prompts.
// Source: huggingface/diffusers

interface GenImage {
    id: string;
    url: string;
    prompt: string;
    negativePrompt: string;
    seed: number;
    steps: number;
    cfgScale: number;
}

export const GenerationGallery: React.FC = () => {
    // Simulated state
    const [images] = useState<GenImage[]>([
        { id: "gen-101", url: "https://via.placeholder.com/512/2c3e50/ffffff?text=Cyberpunk+City", prompt: "A cyberpunk city at night, neon lights, 4k", negativePrompt: "blurry, low res", seed: 489234, steps: 50, cfgScale: 7.5 },
        { id: "gen-102", url: "https://via.placeholder.com/512/8e44ad/ffffff?text=Fantasy+Landscape", prompt: "A fantasy landscape with floating islands, digital art", negativePrompt: "watermark, text", seed: 102938, steps: 30, cfgScale: 6.0 },
        { id: "gen-103", url: "https://via.placeholder.com/512/27ae60/ffffff?text=Astronaut+in+Jungle", prompt: "An astronaut exploring a dense alien jungle", negativePrompt: "distorted, extra limbs", seed: 554321, steps: 40, cfgScale: 8.0 },
    ]);

    const [selectedImage, setSelectedImage] = useState<GenImage | null>(null);

    return (
        <div style={{ padding: '20px', fontFamily: 'Inter, sans-serif', backgroundColor: '#121212', color: '#fff', minHeight: '100vh' }}>
            <h1 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>Stable Diffusion Gallery</h1>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '20px', marginTop: '20px' }}>
                {images.map(img => (
                    <div 
                        key={img.id} 
                        style={{ cursor: 'pointer', borderRadius: '8px', overflow: 'hidden', backgroundColor: '#1e1e1e', transition: 'transform 0.2s' }}
                        onClick={() => setSelectedImage(img)}
                        onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                        onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                    >
                        <img src={img.url} alt={img.prompt} style={{ width: '100%', display: 'block' }} />
                        <div style={{ padding: '10px', fontSize: '0.9em', color: '#aaa', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {img.prompt}
                        </div>
                    </div>
                ))}
            </div>

            {selectedImage && (
                <div style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', backgroundColor: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }} onClick={() => setSelectedImage(null)}>
                    <div style={{ backgroundColor: '#1e1e1e', padding: '20px', borderRadius: '8px', display: 'flex', gap: '20px', maxWidth: '900px', width: '90%' }} onClick={e => e.stopPropagation()}>
                        <img src={selectedImage.url} alt={selectedImage.prompt} style={{ width: '512px', height: '512px', objectFit: 'cover', borderRadius: '4px' }} />
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '15px' }}>
                            <h2 style={{ margin: 0, color: '#4caf50' }}>Generation Details</h2>
                            <div><strong>Prompt:</strong><br/>{selectedImage.prompt}</div>
                            <div><strong>Negative Prompt:</strong><br/>{selectedImage.negativePrompt}</div>
                            <div><strong>Seed:</strong> {selectedImage.seed}</div>
                            <div><strong>Steps:</strong> {selectedImage.steps}</div>
                            <div><strong>CFG Scale:</strong> {selectedImage.cfgScale}</div>
                            <button style={{ marginTop: 'auto', padding: '10px', backgroundColor: '#e74c3c', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }} onClick={() => setSelectedImage(null)}>Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
