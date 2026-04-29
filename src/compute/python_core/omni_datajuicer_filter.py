from typing import List

class OmniDataJuicerFilter:
    """OMNI Compute Layer: DataJuicer Quality Filter (Zero-Mock)"""
    
    def __init__(self, min_word_count: int, max_word_count: int):
        self.min_words = min_word_count
        self.max_words = max_word_count

    def filter_dataset(self, documents: List[str]) -> List[str]:
        filtered = []
        for doc in documents:
            words = len(doc.split())
            if self.min_words <= words <= self.max_words:
                # Alphanumeric ratio check
                alnum_count = sum(c.isalnum() for c in doc)
                if len(doc) > 0 and (alnum_count / len(doc)) > 0.5:
                    filtered.append(doc)
        return filtered
