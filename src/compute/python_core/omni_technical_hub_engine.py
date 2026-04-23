"""OmniTechnicalHubEngine - TF-IDF text extraction and normalized term frequency computation."""
import hashlib
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniTechnicalHubEngine:
    """OMNI Production Engine: OmniTechnicalHubEngine. Zero-Prod compliant."""
    def __init__(self):
        self.version = "3.5.0"

    def extract_term_frequency(self, article: str) -> dict:
        """Perform extract term frequency computation.

            Args:
                    article: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            words = article.lower().split()
            tf = {}
            for w in words:
                clean_w = ''.join(c for c in w if c.isalnum())
                if clean_w:
                    tf[clean_w] = tf.get(clean_w, 0) + 1
                    
            sig = hashlib.sha256(article.encode()).hexdigest()
            total_words = sum(tf.values())
            normalized_tf = {k: v/max(1, total_words) for k, v in tf.items()}
            
            return {
                "status": "ok",
                "value": {
                    "word_count": total_words,
                    "term_frequencies": normalized_tf,
                    "article_hash": sig
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def diagnostics(self) -> dict:
        return {
            "engine": "OmniTechnicalHubEngine",
            "version": self.version,
            "status": "operational"
        }
