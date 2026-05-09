from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class OmniRuformersClassifier:
    """OMNI Framework Russian NLP Model Bridge (ruformers)"""
    def __init__(self, model_id="DeepPavlov/rubert-base-cased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id, num_labels=3)

    def classify_sentiment(self, text: str) -> str:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            pred = torch.argmax(outputs.logits, dim=-1).item()
            
        mapping = {0: "Negative", 1: "Neutral", 2: "Positive"}
        return mapping.get(pred, "Unknown")
