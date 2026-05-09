import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

class OmniFinBertCryptoSentiment(nn.Module):
    """
    OMNI Framework - FinBERT Crypto Sentiment Tracker
    Zero-mock implementation inspired by twitter-alpha-sentiment-tracker-v2.
    Analyzes text and emits Buy/Sell signals based on FinBERT confidence scores.
    """
    def __init__(self, model_name: str = "ProsusAI/finbert", threshold: float = 0.75):
        super(OmniFinBertCryptoSentiment, self).__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.threshold = threshold
        self.labels = ["positive", "negative", "neutral"]

    def forward(self, text_batch: list[str]) -> list[dict]:
        inputs = self.tokenizer(text_batch, padding=True, truncation=True, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        results = []
        for prob in probs:
            pos_score = prob[0].item()
            neg_score = prob[1].item()
            neu_score = prob[2].item()

            signal = "HOLD"
            if pos_score >= self.threshold:
                signal = "BUY"
            elif neg_score >= self.threshold:
                signal = "SELL"

            results.append({
                "signal": signal,
                "confidence": max(pos_score, neg_score, neu_score),
                "scores": {"positive": pos_score, "negative": neg_score, "neutral": neu_score}
            })
        
        return results

def process_crypto_sentiment(tweets: list[str]) -> list[dict]:
    analyzer = OmniFinBertCryptoSentiment()
    return analyzer(tweets)
