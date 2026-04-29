from transformers import pipeline
from typing import List
from omni_core.result import OmniResult, Ok, Err

class PaperSummarizer:
    """
    OMNI COMPUTE LAYER: AI Literature
    Uses HuggingFace Transformers to summarize long academic abstracts.
    """
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        try:
            self.summarizer = pipeline("summarization", model=model_name)
        except Exception as e:
            self.summarizer = None
            print(f"Warning: Model load failed. {e}")

    def summarize_abstracts(self, abstracts: List[str]) -> OmniResult[List[str], str]:
        if not self.summarizer:
            return Err("Summarizer pipeline is not initialized.")
            
        try:
            results = []
            for abstract in abstracts:
                # Truncate to avoid exceeding max input length
                input_text = abstract[:1024]
                summary = self.summarizer(input_text, max_length=130, min_length=30, do_sample=False)
                results.append(summary[0]['summary_text'])
                
            return Ok(results)
        except Exception as e:
            return Err(f"Summarization failed: {str(e)}")
