import torch
from typing import Dict, Any, Optional, List
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class Result:
    def __init__(self, value: Any = None, error: Optional[Exception] = None):
        self.value = value
        self.error = error
        self.is_success = error is None

    @classmethod
    def ok(cls, value: Any) -> 'Result':
        return cls(value=value)

    @classmethod
    def fail(cls, error: Exception) -> 'Result':
        return cls(error=error)

class OmniHanBertEngine:
    """
    OMNI Compute Layer: Korean NLP Engine using HanBert.
    Based on monologg/HanBert-Transformers.
    Optimized for Korean language understanding and sentiment analysis.
    """
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config.get("model_name", "monologg/kobert") # Using kobert as accessible alternative if HanBert not in hub
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_labels = config.get("num_labels", 2)
        self.tokenizer = None
        self.model = None

    def initialize(self) -> Result:
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, 
                num_labels=self.num_labels
            ).to(self.device)
            return Result.ok(True)
        except Exception as e:
            return Result.fail(e)

    def analyze_sentiment(self, text: str) -> Result:
        if not self.model or not self.tokenizer:
            return Result.fail(RuntimeError("Engine not initialized."))
            
        try:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
            
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
            probs = torch.softmax(logits, dim=-1)
            prediction = torch.argmax(probs, dim=-1).item()
            
            return Result.ok({
                "label_id": prediction,
                "confidence": probs[0][prediction].item(),
                "probabilities": probs[0].cpu().tolist()
            })
        except Exception as e:
            return Result.fail(e)

def build_hanbert_engine() -> Result:
    config = {"model_name": "monologg/kobert"}
    engine = OmniHanBertEngine(config)
    return engine.initialize()
