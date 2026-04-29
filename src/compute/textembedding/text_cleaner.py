import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from omni_core.result import OmniResult, Ok, Err

class TextCleaner:
    """
    OMNI COMPUTE LAYER: Text Preprocessing & Embedding
    Cleans text by removing HTML tags, URLs, and punctuation, then applies TF-IDF.
    """
    def __init__(self, max_features: int = 10000):
        self.vectorizer = TfidfVectorizer(max_features=max_features, stop_words='english')
        self.is_fitted = False

    def clean_text(self, text_list: List[str]) -> OmniResult[List[str], str]:
        try:
            cleaned = []
            for text in text_list:
                text = re.sub(r'<[^>]+>', '', text) # Remove HTML
                text = re.sub(r'http\S+', '', text) # Remove URLs
                text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
                cleaned.append(text.lower().strip())
            return Ok(cleaned)
        except Exception as e:
            return Err(f"Text cleaning failed: {str(e)}")

    def compute_tfidf(self, cleaned_texts: List[str]) -> OmniResult[List[List[float]], str]:
        try:
            if not self.is_fitted:
                tfidf_matrix = self.vectorizer.fit_transform(cleaned_texts)
                self.is_fitted = True
            else:
                tfidf_matrix = self.vectorizer.transform(cleaned_texts)
                
            return Ok(tfidf_matrix.toarray().tolist())
        except Exception as e:
            return Err(f"TF-IDF computation failed: {str(e)}")
