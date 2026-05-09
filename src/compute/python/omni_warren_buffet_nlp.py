import pandas as pd
from transformers import pipeline

class OmniWarrenBuffetAnalyzer:
    """OMNI Framework NLP Pipeline for Warren Buffet Letters Analysis"""
    
    def __init__(self):
        # Initialize a pre-trained financial sentiment model
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis", 
            model="ProsusAI/finbert"
        )
        self.ner_analyzer = pipeline(
            "ner", 
            model="dslim/bert-base-NER", 
            aggregation_strategy="simple"
        )

    def analyze_letter(self, text: str) -> dict:
        """Performs sentiment analysis and entity extraction on letter text."""
        sentiment = self.sentiment_analyzer(text[:512])[0]
        entities = self.ner_analyzer(text[:512])
        
        return {
            "sentiment": sentiment['label'],
            "confidence": sentiment['score'],
            "entities": [{"word": e['word'], "entity_group": e['entity_group']} for e in entities]
        }

    def process_batch(self, letters: list) -> pd.DataFrame:
        results = [self.analyze_letter(letter) for letter in letters]
        return pd.DataFrame(results)
