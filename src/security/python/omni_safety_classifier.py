"""
OMNI Compute — Safety Classifier & Content Filter
Production content moderation for inference outputs.
"""
import re, logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger("omni.safety")

class RiskLevel(Enum):
    SAFE = "safe"; LOW = "low"; MEDIUM = "medium"; HIGH = "high"; CRITICAL = "critical"

@dataclass
class SafetyResult:
    is_safe: bool; risk_level: RiskLevel; categories: Dict[str, float] = field(default_factory=dict)
    flagged_patterns: List[str] = field(default_factory=list); explanation: str = ""

@dataclass
class SafetyConfig:
    enable_pii_detection: bool = True; enable_toxicity: bool = True
    enable_prompt_injection: bool = True; enable_jailbreak: bool = True
    risk_threshold: float = 0.7; block_critical: bool = True

class OmniSafetyClassifier:
    """Production safety classifier for LLM inputs and outputs."""
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }
    INJECTION_PATTERNS = [
        r'ignore\s+(?:all\s+)?(?:previous|above|prior)\s+instructions',
        r'forget\s+(?:all\s+)?(?:previous|your)\s+(?:instructions|rules)',
        r'you\s+are\s+now\s+(?:a|an)\s+(?:different|new)',
        r'system\s*:\s*you\s+are',
        r'<\|system\|>',
        r'###\s*(?:system|instruction)',
    ]
    TOXIC_KEYWORDS = ["hate", "kill", "violent", "racist", "sexist", "bomb", "weapon", "exploit"]

    def __init__(self, config: SafetyConfig = SafetyConfig()):
        self.config = config; self.stats = {"total": 0, "blocked": 0, "pii_detected": 0}

    def classify(self, text: str) -> SafetyResult:
        self.stats["total"] += 1
        categories = {}; flagged = []
        if self.config.enable_pii_detection:
            pii_score, pii_found = self._check_pii(text)
            categories["pii"] = pii_score; flagged.extend(pii_found)
        if self.config.enable_prompt_injection:
            inj_score = self._check_injection(text)
            categories["prompt_injection"] = inj_score
            if inj_score > 0.5: flagged.append("prompt_injection_detected")
        if self.config.enable_toxicity:
            tox_score = self._check_toxicity(text)
            categories["toxicity"] = tox_score
        if self.config.enable_jailbreak:
            jb_score = self._check_jailbreak(text)
            categories["jailbreak"] = jb_score

        max_score = max(categories.values()) if categories else 0.0
        if max_score >= 0.9: risk = RiskLevel.CRITICAL
        elif max_score >= 0.7: risk = RiskLevel.HIGH
        elif max_score >= 0.4: risk = RiskLevel.MEDIUM
        elif max_score >= 0.1: risk = RiskLevel.LOW
        else: risk = RiskLevel.SAFE

        is_safe = max_score < self.config.risk_threshold
        if not is_safe: self.stats["blocked"] += 1

        return SafetyResult(is_safe=is_safe, risk_level=risk, categories=categories,
                           flagged_patterns=flagged)

    def _check_pii(self, text: str) -> Tuple[float, List[str]]:
        found = []
        for name, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, text): found.append(f"pii:{name}")
        if found: self.stats["pii_detected"] += 1
        return min(len(found) * 0.3, 1.0), found

    def _check_injection(self, text: str) -> float:
        text_lower = text.lower()
        matches = sum(1 for p in self.INJECTION_PATTERNS if re.search(p, text_lower, re.IGNORECASE))
        return min(matches * 0.4, 1.0)

    def _check_toxicity(self, text: str) -> float:
        text_lower = text.lower()
        matches = sum(1 for kw in self.TOXIC_KEYWORDS if kw in text_lower)
        return min(matches * 0.2, 1.0)

    def _check_jailbreak(self, text: str) -> float:
        indicators = ["DAN", "developer mode", "no restrictions", "bypass", "pretend you"]
        text_lower = text.lower()
        return min(sum(0.3 for i in indicators if i.lower() in text_lower), 1.0)

    def get_stats(self) -> Dict:
        return {**self.stats, "block_rate": self.stats["blocked"]/max(self.stats["total"],1)}
