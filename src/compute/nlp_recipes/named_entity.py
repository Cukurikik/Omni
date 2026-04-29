from transformers import AutoModelForTokenClassification, AutoTokenizer

class NERModel:
    def __init__(self, model_name="dbmdz/bert-large-cased-finetuned-conll03-english"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        
    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)
        predictions = outputs.logits.argmax(dim=-1)
        
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        return list(zip(tokens, predictions[0].tolist()))
