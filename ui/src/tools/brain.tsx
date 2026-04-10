import React, { useState } from 'react';
import { useOmniJob } from '../hooks/useOmniJob';
import { OmniClient } from '../lib/omni-client'; // Menggunakan SDK OMNI!

// Skuad Frontend: Fokus di sini! Backend sudah diurus otomatis.
export default function brainUI() {
    const [file, setFile] = useState(null as File | null);
    const [jobId, setJobId] = useState(null as string | null);
    const { progress, status } = useOmniJob(jobId); // Hook otomatis ke WebSocket

    const handleExecute = async () => {
        if (!file) return;
        // Panggil SDK, tak perlu pusing soal fetch, FormData, atau Headers!
        const result = await OmniClient.processFile("brain", file);
        setJobId(result.job_id);
    };

    return (
        <div className="p-4 bg-gray-800 rounded">
            <h2 className="text-xl font-bold">BRAIN</h2>
            <input type="file" onChange={e => setFile(e.target.files?.[0] || null)} />
            <button onClick={handleExecute} className="bg-blue-500 p-2 mt-2">Eksekusi</button>
            <p>Status: {status} | Progress: {progress}%</p>
        </div>
    );
}
