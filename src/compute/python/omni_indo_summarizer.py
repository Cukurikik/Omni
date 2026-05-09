from transformers import EncoderDecoderModel, AutoTokenizer

class OmniIndoSummarizer:
    """OMNI Framework Abstractive Summarizer for Indonesian (Liputan6)"""
    
    def __init__(self, model_name="cahya/bert2bert-indonesian-summarization"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = EncoderDecoderModel.from_pretrained(model_name)

    def summarize(self, text: str) -> str:
        input_ids = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True).input_ids
        output_ids = self.model.generate(
            input_ids, 
            max_length=150, 
            min_length=40, 
            length_penalty=2.0, 
            num_beams=4
        )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
