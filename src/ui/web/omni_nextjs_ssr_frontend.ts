// OMNI UI Layer
// Next.js SSR Frontend Integration
// Based on vercel/next.js. Connects Server-Side Rendered React apps to the Omni Engine.

import { GetServerSideProps } from 'next';
import Head from 'next/head';
import React from 'react';

// Simulated C-ABI / IPC client for Next.js server context
const fetchOmniServerSideState = async () => {
    // This executes ON THE SERVER (Node.js runtime), 
    // communicating directly with the Universal Binary via Unix Sockets or HTTP
    console.log("OMNI TS (Server): Fetching initial cluster state via IPC...");
    
    return {
        clusterHealth: 'Healthy',
        activeNodes: 142,
        throughputTps: 8500
    };
};

interface OmniDashboardProps {
    initialState: {
        clusterHealth: string;
        activeNodes: number;
        throughputTps: number;
    };
}

export default function OmniDashboard({ initialState }: OmniDashboardProps) {
    return (
        <div className="omni-nextjs-container">
            <Head>
                <title>OMNI SSR Dashboard</title>
                <meta name="description" content="Next.js interface to Universal Binary" />
            </Head>

            <main>
                <h1 className="text-4xl font-bold">OMNI Universal Engine</h1>
                <p className="mt-2 text-gray-600">Server-Side Rendered Metrics</p>

                <div className="grid grid-cols-3 gap-4 mt-8">
                    <div className="card">
                        <h3>Health</h3>
                        <p className={initialState.clusterHealth === 'Healthy' ? 'text-green-500' : 'text-red-500'}>
                            {initialState.clusterHealth}
                        </p>
                    </div>
                    <div className="card">
                        <h3>Active Nodes</h3>
                        <p>{initialState.activeNodes}</p>
                    </div>
                    <div className="card">
                        <h3>Throughput (TPS)</h3>
                        <p>{initialState.throughputTps.toLocaleString()}</p>
                    </div>
                </div>
            </main>
        </div>
    );
}

export const getServerSideProps: GetServerSideProps = async (context) => {
    try {
        const initialState = await fetchOmniServerSideState();
        return {
            props: {
                initialState
            }
        };
    } catch (error) {
        console.error("OMNI SSR Error:", error);
        return {
            props: {
                initialState: { clusterHealth: 'Unknown', activeNodes: 0, throughputTps: 0 }
            }
        };
    }
};
