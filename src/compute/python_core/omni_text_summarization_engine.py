import torch
from typing import Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

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

class OmniTextSummarizationEngine:
    """
    OMNI Compute Layer: Abstractive Text Summarization Engine.
    Uses BART/T5 models for high-quality sequence-to-sequence summarization.
    Based on aj-naik/Text-Summarization.
    """
    def __init__(self, config: Dict[str, Any]):
        # e.g., facebook/bart-large-cnn
        self.model_name = config.get("model_name", "facebook/bart-large-cnn")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = None
        self.model = None

    def initialize(self) -> Result:
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
            return Result.ok(True)
        except Exception as e:
            return Result.fail(e)

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30) -> Result:
        if not self.model or not self.tokenizer:
            return Result.fail(RuntimeError("Engine not initialized. Call initialize() first."))
            
        try:
            inputs = self.tokenizer([text], max_length=1024, return_tensors="pt", truncation=True).to(self.device)
            
            # Generate summary with beam search
            summary_ids = self.model.generate(
                inputs["input_ids"],
                num_beams=4,
                max_length=max_length,
                min_length=min_length,
                early_stopping=True,
                no_repeat_ngram_size=3
            )
            
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
            
            return Result.ok(summary)
        except Exception as e:
            return Result.fail(e)

def build_summarization_engine() -> Result:
    config = {"model_name": "facebook/bart-large-cnn"}
    engine = OmniTextSummarizationEngine(config)
    return engine.initialize()
