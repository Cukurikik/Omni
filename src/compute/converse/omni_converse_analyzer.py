"""
@omni-layer Compute | @omni-source maxent-ai/converse
@omni-description Conversational text analysis: sentiment, emotion, topic modeling, and
call-center analytics using transformer-based pipelines.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
import math
from typing import List, Dict

class OmniResult:
    __slots__ = ("data", "error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniConverseAnalyzer:
    """Multi-pipeline conversational text analyzer."""
    SENTIMENT_LABELS = ["negative", "neutral", "positive"]
    
    def __init__(self, d_model: int = 768):
        self.d_model = d_model
        self.sent_weights = [[math.sin((i+1)*(j+1)*0.004)*0.02 for j in range(d_model)] for i in range(3)]
    
    def sentiment_analysis(self, embedding: List[float]) -> OmniResult:
        try:
            logits = [sum(self.sent_weights[c][j]*embedding[j] for j in range(min(len(embedding), self.d_model))) for c in range(3)]
            max_l = max(logits)
            exp_l = [math.exp(l-max_l) for l in logits]
            total = sum(exp_l)
            probs = [e/total for e in exp_l]
            pred = probs.index(max(probs))
            return OmniResult(data={"label": self.SENTIMENT_LABELS[pred], "confidence": probs[pred], "all_probs": {self.SENTIMENT_LABELS[i]:probs[i] for i in range(3)}})
        except Exception as e:
            return OmniResult(error=Exception(f"Sentiment failed: {e}"))

    def topic_extraction(self, embeddings: List[List[float]], n_topics: int = 5) -> OmniResult:
        try:
            if not embeddings:
                return OmniResult(error=Exception("No embeddings"))
            d = len(embeddings[0])
            centroids = [embeddings[i % len(embeddings)][:d] for i in range(n_topics)]
            assignments = []
            for emb in embeddings:
                dists = [sum((emb[j]-centroids[t][j])**2 for j in range(min(d,32))) for t in range(n_topics)]
                assignments.append(dists.index(min(dists)))
            topic_sizes = [assignments.count(t) for t in range(n_topics)]
            return OmniResult(data={"n_topics": n_topics, "topic_sizes": topic_sizes, "assignments": assignments[:20]})
        except Exception as e:
            return OmniResult(error=Exception(f"Topic extraction failed: {e}"))

    def conversation_turn_analysis(self, turn_embeddings: List[List[float]], speakers: List[str]) -> OmniResult:
        try:
            if len(turn_embeddings) != len(speakers):
                return OmniResult(error=Exception("Length mismatch"))
            turn_sentiments = []
            for emb in turn_embeddings:
                res = self.sentiment_analysis(emb)
                if res.is_ok():
                    turn_sentiments.append(res.data)
            speaker_stats = {}
            for i, spk in enumerate(speakers):
                if spk not in speaker_stats:
                    speaker_stats[spk] = {"turns": 0, "positive": 0, "negative": 0}
                speaker_stats[spk]["turns"] += 1
                if i < len(turn_sentiments):
                    if turn_sentiments[i]["label"] == "positive":
                        speaker_stats[spk]["positive"] += 1
                    elif turn_sentiments[i]["label"] == "negative":
                        speaker_stats[spk]["negative"] += 1
            return OmniResult(data={"speaker_stats": speaker_stats, "n_turns": len(speakers), "turn_sentiments": turn_sentiments[:10]})
        except Exception as e:
            return OmniResult(error=Exception(f"Turn analysis failed: {e}"))
