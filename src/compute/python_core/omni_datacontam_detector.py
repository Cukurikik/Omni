import hashlib

class OmniDataContamDetector:
    """OMNI Compute Layer: Data Contamination Detector"""
    
    def __init__(self, n_gram: int = 8):
        self.n_gram = n_gram

    def detect_overlap(self, test_set: str, training_corpus: str) -> float:
        if not test_set or not training_corpus:
            return 0.0
            
        # Deterministic basic n-gram overlap check
        test_words = test_set.split()
        if len(test_words) < self.n_gram:
            return 1.0 if test_set in training_corpus else 0.0
            
        overlaps = 0
        total_ngrams = len(test_words) - self.n_gram + 1
        
        for i in range(total_ngrams):
            ngram = " ".join(test_words[i:i+self.n_gram])
            if ngram in training_corpus:
                overlaps += 1
                
        return overlaps / float(total_ngrams)
