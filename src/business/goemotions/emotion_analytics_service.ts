// @omni-layer Business | @omni-source monologg/GoEmotions-pytorch
// @omni-description Emotion analytics API in TypeScript: RESTful service for
// multi-label emotion detection with batch processing.
// @omni-lang TypeScript | @omni-batch 16 | @omni-semester 16

interface EmotionPrediction {
  label: string;
  probability: number;
  logit: number;
}

interface AnalyticsRequest {
  text_id: string;
  embedding: number[];
  metadata?: Record<string, string>;
}

interface AnalyticsResponse {
  text_id: string;
  emotions: EmotionPrediction[];
  dominant_emotion: string;
  sentiment_valence: number;
  processing_ms: number;
}

interface OmniResult<T> { data?: T; error?: string; }

const EMOTION_LABELS = [
  "admiration","amusement","anger","annoyance","approval","caring","confusion",
  "curiosity","desire","disappointment","disapproval","disgust","embarrassment",
  "excitement","fear","gratitude","grief","joy","love","nervousness","optimism",
  "pride","realization","relief","remorse","sadness","surprise","neutral"
];

const VALENCE_MAP: Record<string, number> = {
  joy: 0.9, love: 0.85, admiration: 0.8, amusement: 0.75, excitement: 0.8,
  gratitude: 0.7, optimism: 0.7, pride: 0.65, relief: 0.6, approval: 0.5,
  caring: 0.5, curiosity: 0.3, realization: 0.2, surprise: 0.1, neutral: 0,
  confusion: -0.2, nervousness: -0.3, disappointment: -0.5, disapproval: -0.5,
  embarrassment: -0.4, annoyance: -0.5, sadness: -0.7, remorse: -0.6,
  fear: -0.7, grief: -0.8, anger: -0.7, disgust: -0.8, desire: 0.4
};

class EmotionAnalyticsService {
  private weights: number[][];
  private threshold: number;

  constructor(dModel: number = 768, threshold: number = 0.3) {
    this.threshold = threshold;
    this.weights = EMOTION_LABELS.map((_, i) =>
      Array.from({length: dModel}, (_, j) => Math.sin((i+1)*(j+1)*0.003) * 0.02)
    );
  }

  analyze(request: AnalyticsRequest): OmniResult<AnalyticsResponse> {
    const start = Date.now();
    try {
      const logits = this.weights.map(w =>
        w.reduce((s, wj, j) => s + wj * (request.embedding[j] || 0), 0)
      );
      const probs = logits.map(l => 1 / (1 + Math.exp(-l)));
      const emotions: EmotionPrediction[] = probs
        .map((p, i) => ({label: EMOTION_LABELS[i], probability: p, logit: logits[i]}))
        .filter(e => e.probability >= this.threshold)
        .sort((a, b) => b.probability - a.probability);
      const dominant = emotions[0]?.label || "neutral";
      const valence = emotions.reduce((s, e) => s + (VALENCE_MAP[e.label] || 0) * e.probability, 0);
      return {data: {text_id: request.text_id, emotions, dominant_emotion: dominant, sentiment_valence: valence, processing_ms: Date.now() - start}};
    } catch (e) {
      return {error: `Analysis failed: ${e}`};
    }
  }

  batchAnalyze(requests: AnalyticsRequest[]): OmniResult<AnalyticsResponse[]> {
    try {
      const results = requests.map(r => this.analyze(r));
      const successes = results.filter(r => r.data).map(r => r.data!);
      return {data: successes};
    } catch (e) { return {error: `Batch failed: ${e}`}; }
  }
}

export { EmotionAnalyticsService, EMOTION_LABELS, VALENCE_MAP };
export type { AnalyticsRequest, AnalyticsResponse, EmotionPrediction };
