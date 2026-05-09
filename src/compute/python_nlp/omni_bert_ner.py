import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification

class OmniBertNER:
    """
    Transformers-NER: Named Entity Recognition using HuggingFace BERT.
    Tokenizes text, infers entities (PER, ORG, LOC, MISC), and re-aligns tokens.
    """
    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        self.id2label = self.model.config.id2label

    def extract_entities(self, text: str) -> list[dict]:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)[0].tolist()
            
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        
        entities = []
        current_entity = ""
        current_type = None
        
        for token, pred_id in zip(tokens, predictions):
            if token in ["[CLS]", "[SEP]", "[PAD]"]:
                continue
                
            label = self.id2label[pred_id]
            
            if label.startswith("B-"):
                if current_entity:
                    entities.append({"entity": current_entity.replace("##", ""), "type": current_type})
                current_entity = token
                current_type = label[2:]
            elif label.startswith("I-") and current_entity:
                current_entity += token
            else:
                if current_entity:
                    entities.append({"entity": current_entity.replace("##", ""), "type": current_type})
                    current_entity = ""
                    current_type = None
                    
        if current_entity:
            entities.append({"entity": current_entity.replace("##", ""), "type": current_type})
            
        return entities
