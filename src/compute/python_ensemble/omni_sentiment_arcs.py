import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class OmniSentimentArcs:
    """
    OMNI Implementation of SentimentArcs.
    Uses an ensemble of multiple transformer models to analyze the emotion of text 
    over a temporal progression (e.g. chapters in a book, scenes in a movie).
    """
    def __init__(self, models: list[str] = ["distilbert-base-uncased-finetuned-sst-2-english", "cardiffnlp/twitter-roberta-base-sentiment"]):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.ensembles = []
        
        for model_name in models:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
            model.eval()
            self.ensembles.append((tokenizer, model))

    def _get_sentiment(self, text: str, tokenizer, model) -> float:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            # Assuming binary or ternary, return a weighted score between -1.0 and 1.0
            if probs.shape[-1] == 2:
                return (probs[0][1] - probs[0][0]).item()
            elif probs.shape[-1] == 3:
                return (probs[0][2] - probs[0][0]).item()
            else:
                return probs[0].argmax().item()

    def analyze_arc(self, temporal_text_blocks: list[str]) -> np.ndarray:
        """
        Takes an ordered list of text blocks and returns the sentiment arc array.
        """
        arc = []
        for block in temporal_text_blocks:
            ensemble_scores = []
            for tokenizer, model in self.ensembles:
                score = self._get_sentiment(block, tokenizer, model)
                ensemble_scores.append(score)
            
            # Average the ensemble predictions for this time step
            arc.append(np.mean(ensemble_scores))
            
        return np.array(arc)
