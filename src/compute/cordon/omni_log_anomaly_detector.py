"""
@omni-layer Compute | @omni-source calebevans/cordon
@omni-description Log anomaly detector: semantic embedding of log lines
with clustering-based anomaly detection and drain-style template extraction.
@omni-lang Python | @omni-batch 17 | @omni-semester 16
"""
import math, re
from typing import List, Dict

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

class OmniLogAnomalyDetector:
    def __init__(self, d=128, threshold=0.3):
        self.d = d; self.threshold = threshold
        self.templates: Dict[str, int] = {}
        self.centroid: List[float] = [0.0]*d
        self.n_seen = 0

    def _tokenize_log(self, line: str) -> str:
        line = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<IP>', line)
        line = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', '<TIMESTAMP>', line)
        line = re.sub(r'0x[0-9a-fA-F]+', '<HEX>', line)
        line = re.sub(r'\b\d+\b', '<NUM>', line)
        return line.strip()

    def _embed(self, text: str) -> List[float]:
        emb = [0.0]*self.d
        for i, ch in enumerate(text[:200]):
            idx = (ord(ch)*(i+1)) % self.d
            emb[idx] += math.sin(ord(ch)*0.05)
        norm = math.sqrt(sum(v*v for v in emb)+1e-8)
        return [v/norm for v in emb]

    def process_line(self, line: str) -> OmniResult:
        try:
            template = self._tokenize_log(line)
            self.templates[template] = self.templates.get(template, 0) + 1
            emb = self._embed(template)
            if self.n_seen == 0:
                self.centroid = emb[:]
            else:
                for i in range(self.d):
                    self.centroid[i] = (self.centroid[i]*self.n_seen + emb[i]) / (self.n_seen+1)
            self.n_seen += 1
            dist = math.sqrt(sum((emb[i]-self.centroid[i])**2 for i in range(self.d)))
            is_anomaly = dist > self.threshold
            return OmniResult(data={"template": template, "distance": dist, "is_anomaly": is_anomaly, "template_count": self.templates[template]})
        except Exception as e: return OmniResult(error=e)

    def analyze_batch(self, lines: List[str]) -> OmniResult:
        try:
            anomalies = []
            for line in lines:
                r = self.process_line(line)
                if r.is_ok() and r.data["is_anomaly"]:
                    anomalies.append(r.data)
            return OmniResult(data={"total_lines": len(lines), "anomalies": len(anomalies), "anomaly_rate": len(anomalies)/max(len(lines),1), "unique_templates": len(self.templates), "top_templates": sorted(self.templates.items(), key=lambda x: -x[1])[:5]})
        except Exception as e: return OmniResult(error=e)
