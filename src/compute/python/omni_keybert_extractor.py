from keybert import KeyBERT

class OmniKeyphraseExtractor:
    """OMNI Framework Keyword Extraction using KeyBERT"""
    def __init__(self):
        # Initialize KeyBERT with a fast multilingual model
        self.kw_model = KeyBERT(model='paraphrase-multilingual-MiniLM-L12-v2')

    def extract_keywords(self, doc: str, top_n: int = 5):
        """Extracts top_n keywords from the document using Maximal Marginal Relevance."""
        keywords = self.kw_model.extract_keywords(
            doc, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english', 
            use_mmr=True, 
            diversity=0.7,
            top_n=top_n
        )
        return [{"keyword": kw[0], "score": kw[1]} for kw in keywords]
