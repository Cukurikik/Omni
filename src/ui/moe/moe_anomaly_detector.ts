// moe_anomaly_detector.ts — Interface / React Hooks
// Layer: Interface / Web — Routing Anomaly Detection
//
// Analyzes the MoE routing distribution to detect "Expert Collapse" 
// (e.g., when the router incorrectly sends 99% of tokens to a single expert).
// Exposes a React hook for dashboards to display alerts.

import { useState, useEffect } from 'react';

export interface RoutingDistribution {
    expertId: number;
    tokenPercentage: number;
}

export interface AnomalyAlert {
    isCollapsing: boolean;
    dominantExpertId: number | null;
    message: string;
}

/**
 * Custom React hook to monitor MoE routing distribution for collapse anomalies.
 */
export function useMoEAnomalyDetector(
    distributions: RoutingDistribution[],
    collapseThreshold: number = 85.0 // If an expert gets >85% load, flag it
): AnomalyAlert {
    const [alert, setAlert] = useState<AnomalyAlert>({
        isCollapsing: false,
        dominantExpertId: null,
        message: 'Routing is balanced.'
    });

    useEffect(() => {
        if (!distributions || distributions.length === 0) return;

        let collapsed = false;
        let domExpert: number | null = null;

        for (const dist of distributions) {
            if (dist.tokenPercentage >= collapseThreshold) {
                collapsed = true;
                domExpert = dist.expertId;
                break;
            }
        }

        if (collapsed) {
            setAlert({
                isCollapsing: true,
                dominantExpertId: domExpert,
                message: `CRITICAL: Expert Collapse Detected! Expert ${domExpert} is handling >${collapseThreshold}% of all tokens. Check router loss.`
            });
        } else {
            setAlert({
                isCollapsing: false,
                dominantExpertId: null,
                message: 'Routing is balanced and healthy.'
            });
        }
    }, [distributions, collapseThreshold]);

    return alert;
}
