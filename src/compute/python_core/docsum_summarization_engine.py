from transformers import BartForConditionalGeneration, BartTokenizer
from typing import Dict, Any

class DocSumEngine:
    """
    DocSum: Automatic document summarization abstractively using BART.
    """
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text: str, max_length: int = 150) -> Dict[str, Any]:
        try:
            inputs = self.tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)
            summary_ids = self.model.generate(inputs["input_ids"], max_length=max_length, num_beams=4, early_stopping=True)
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return {"status": "success", "summary": summary}
        except Exception as e:
            return {"status": "error", "message": str(e), "summary": None}
