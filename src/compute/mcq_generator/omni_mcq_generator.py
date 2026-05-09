# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo Leaf-Question-Generation + X-Transformer
# @omni-description MCQ generator: extract key concepts from text, generate
# questions with distractors using transformer-based semantic similarity.

import math
from typing import Dict, List, Tuple

class ConceptExtractor:
    """Extracts key concepts from text using TF-IDF-like scoring."""
    def __init__(self):
        self.stop_words = {"the","a","an","is","are","was","were","be","been",
                           "being","have","has","had","do","does","did","will",
                           "would","could","should","may","might","can","shall",
                           "in","on","at","to","for","of","with","by","from",
                           "and","or","but","not","no","this","that","it","its"}

    def extract(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        words = [w.strip('.,!?;:').lower() for w in text.split()]
        words = [w for w in words if w and w not in self.stop_words and len(w) > 2]
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        max_freq = max(freq.values()) if freq else 1
        scored = [(w, f/max_freq * (1 + math.log(len(w)))) for w, f in freq.items()]
        scored.sort(key=lambda x: -x[1])
        return scored[:top_k]

class DistractorGenerator:
    """Generates plausible distractors using semantic distance."""
    def __init__(self, d: int = 128):
        self.d = d

    def embed_word(self, word: str) -> List[float]:
        emb = [0.0] * self.d
        for i, c in enumerate(word[:50]):
            idx = (ord(c) * (i + 1)) % self.d
            emb[idx] += math.sin(ord(c) * 0.1) * 0.1
        norm = math.sqrt(sum(e*e for e in emb)) + 1e-10
        return [e/norm for e in emb]

    def generate(self, answer: str, context_words: List[str], n: int = 3) -> List[str]:
        answer_emb = self.embed_word(answer)
        candidates = []
        for word in context_words:
            if word.lower() == answer.lower():
                continue
            w_emb = self.embed_word(word)
            sim = sum(a*b for a, b in zip(answer_emb, w_emb))
            if 0.2 < sim < 0.8:
                candidates.append((word, sim))
        candidates.sort(key=lambda x: -x[1])
        result = [c[0] for c in candidates[:n]]
        while len(result) < n:
            h = sum(ord(c) * (i+1) for i, c in enumerate(answer)) + len(result)
            result.append(f"option_{h % 10000}")
        return result

class MCQGenerator:
    """Generate multiple-choice questions from text."""
    def __init__(self):
        self.extractor = ConceptExtractor()
        self.distractor_gen = DistractorGenerator()

    def generate(self, text: str, n_questions: int = 5) -> List[Dict]:
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        concepts = self.extractor.extract(text, top_k=20)
        concept_words = [c[0] for c in concepts]
        questions = []
        for i, sent in enumerate(sentences[:n_questions * 2]):
            words = sent.split()
            if len(words) < 5:
                continue
            answer_candidates = [w.strip('.,!?').lower() for w in words
                                if w.strip('.,!?').lower() in concept_words]
            if not answer_candidates:
                continue
            answer = answer_candidates[0]
            q_text = sent.replace(answer, "______", 1)
            distractors = self.distractor_gen.generate(answer, concept_words)
            questions.append({
                "question": q_text + "?",
                "answer": answer,
                "distractors": distractors,
                "source": sent,
                "difficulty": min(1.0, len(answer) * 0.1 + len(words) * 0.02),
            })
            if len(questions) >= n_questions:
                break
        return questions
