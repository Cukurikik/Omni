/**
 * OMNI MMTS-GEE Temporal Aligner — Concurrency Layer
 * Absorbing palubad/MMTS-GEE multi-modal multi-temporal satellite dataset generation.
 * JavaScript event-loop aligned temporal matching for Earth Engine style data fusion.
 */

class OmniMmtsGeeAligner {
  constructor() {
    this.temporalIndex = new Map();
    this.alignments = 0;
  }

  registerObservation(sensorId, timestamp, bands) {
    if (!sensorId || !timestamp || !Array.isArray(bands)) {
      return { ok: false, error: 'MMTSError: Invalid observation parameters' };
    }
    const key = `${sensorId}:${timestamp}`;
    this.temporalIndex.set(key, { sensorId, timestamp, bands, registeredAt: Date.now() });
    return { ok: true, registered: key };
  }

  findTemporalMatch(targetTimestamp, maxDeltaMs, sensorA, sensorB) {
    if (!targetTimestamp || maxDeltaMs <= 0) {
      return { ok: false, error: 'MMTSError: Invalid temporal search criteria' };
    }

    this.alignments++;
    let bestA = null, bestB = null;
    let bestDeltaA = Infinity, bestDeltaB = Infinity;

    for (const [, obs] of this.temporalIndex) {
      const delta = Math.abs(obs.timestamp - targetTimestamp);
      if (delta > maxDeltaMs) continue;

      if (obs.sensorId === sensorA && delta < bestDeltaA) {
        bestDeltaA = delta;
        bestA = obs;
      }
      if (obs.sensorId === sensorB && delta < bestDeltaB) {
        bestDeltaB = delta;
        bestB = obs;
      }
    }

    if (!bestA || !bestB) {
      return { ok: false, error: 'MMTSError: Could not find matching pair within temporal window' };
    }

    return {
      ok: true,
      pair: { sensorA: bestA, sensorB: bestB },
      temporalGap: Math.abs(bestA.timestamp - bestB.timestamp)
    };
  }

  diagnostics() {
    return {
      engine: 'OmniMmtsGeeAligner',
      observations: this.temporalIndex.size,
      alignments: this.alignments,
      status: 'Operational'
    };
  }
}

export default OmniMmtsGeeAligner;
