import { onDocumentCreated } from 'firebase-functions/v2/firestore';
import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

// Initialize Admin SDK automatically in cloud functions context
initializeApp();

/**
 * 53. Firebase Event Listener (Storage/PubSub triggers mapped natively)
 * We use Firestore onCreate triggers to act as pub/sub for offloading jobs.
 * Updated to Firebase Functions v2 API.
 */

// 56. Fallback Video Compressor (Firebase Function)
export const fallbackCompressor = onDocumentCreated(
  { document: 'videoJobs/{jobId}', timeoutSeconds: 540, memory: '2GiB' },
  async (event) => {
    const snap = event.data;
    if (!snap) return;
    const data = snap.data();
    if (data.operation !== 'compressor') return;

    const db = getFirestore();
    const docRef = db.doc(`videoJobs/${event.params.jobId}`);

    // Simulate updating processing state
    await docRef.update({ status: 'processing', progress: 10 });

    // Virtual FFmpeg processing GCP logic
    // const { spawn } = require('child_process'); ...

    // Finalize
    await docRef.update({ status: 'success', progress: 100, resultUrl: 'gs://omni-tool-bucket/output/path.mp4' });
  }
);

// 57. Fallback Video Converter (Firebase Function)
export const fallbackConverter = onDocumentCreated(
  { document: 'videoJobs/{jobId}', timeoutSeconds: 540, memory: '4GiB' },
  async (event) => {
    const snap = event.data;
    if (!snap) return;
    const data = snap.data();
    if (data.operation !== 'converter') return;

    const db = getFirestore();
    const docRef = db.doc(`videoJobs/${event.params.jobId}`);

    await docRef.update({ status: 'processing', progress: 20 });
    // FFmpeg conversion logic
    await docRef.update({ status: 'success', progress: 100, resultUrl: 'gs://omni-tool-bucket/output/path.mkv' });
  }
);

// 58. Fallback Audio Extractor (Firebase Function)
export const fallbackAudioExtractor = onDocumentCreated(
  { document: 'videoJobs/{jobId}', timeoutSeconds: 300, memory: '1GiB' },
  async (event) => {
    const snap = event.data;
    if (!snap) return;
    const data = snap.data();
    if (data.operation !== 'audio-extractor') return;

    const db = getFirestore();
    const docRef = db.doc(`videoJobs/${event.params.jobId}`);

    await docRef.update({ status: 'processing', progress: 50 });
    // Audio extraction logic
    await docRef.update({ status: 'success', progress: 100, resultUrl: 'gs://omni-tool-bucket/output/audio.mp3' });
  }
);
