/**
 * OMNI Semantic Image Search Engine — Concurrency Layer
 * Absorbing aws-samples/semantic-image-search-for-articles
 * Async event-loop driven vector similarity search dispatcher.
 */

class OmniSemanticImageSearch {
  constructor(maxResults = 10) {
    this.maxResults = maxResults;
    this.indexedImages = [];
    this.queries = 0;
  }

  indexImage(imageId, embeddingVector) {
    if (!imageId || !Array.isArray(embeddingVector) || embeddingVector.length === 0) {
      return { ok: false, error: 'SemanticSearchError: Invalid image or empty embedding' };
    }
    const norm = Math.sqrt(embeddingVector.reduce((s, v) => s + v * v, 0));
    const normalized = norm > 0 ? embeddingVector.map(v => v / norm) : embeddingVector;
    this.indexedImages.push({ id: imageId, vec: normalized });
    return { ok: true, totalIndexed: this.indexedImages.length };
  }

  async searchByVector(queryVector, topK) {
    if (!Array.isArray(queryVector) || queryVector.length === 0) {
      return { ok: false, error: 'SemanticSearchError: Empty query vector' };
    }
    if (this.indexedImages.length === 0) {
      return { ok: false, error: 'SemanticSearchError: Index is empty' };
    }

    this.queries++;
    const k = Math.min(topK || this.maxResults, this.indexedImages.length);
    const qNorm = Math.sqrt(queryVector.reduce((s, v) => s + v * v, 0));
    const qNormalized = qNorm > 0 ? queryVector.map(v => v / qNorm) : queryVector;

    // Cosine similarity via dot product (both vectors L2-normalized)
    const scores = this.indexedImages.map((img, idx) => {
      let dot = 0;
      const minLen = Math.min(qNormalized.length, img.vec.length);
      for (let i = 0; i < minLen; i++) {
        dot += qNormalized[i] * img.vec[i];
      }
      return { index: idx, id: img.id, score: dot };
    });

    scores.sort((a, b) => b.score - a.score);
    const topResults = scores.slice(0, k);

    return { ok: true, results: topResults };
  }

  diagnostics() {
    return {
      engine: 'OmniSemanticImageSearch',
      indexed: this.indexedImages.length,
      queries: this.queries,
      status: 'Operational'
    };
  }
}

export default OmniSemanticImageSearch;
