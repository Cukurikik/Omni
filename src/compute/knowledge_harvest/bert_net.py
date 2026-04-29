from typing import List, Tuple
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer

class BertNetHarvester:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        self.model = AutoModelForMaskedLM.from_pretrained("bert-base-uncased")

    def harvest_relation(self, subject: str, relation_template: str) -> List[Tuple[str, float]]:
        text = relation_template.replace("[X]", subject).replace("[Y]", self.tokenizer.mask_token)
        inputs = self.tokenizer(text, return_tensors="pt")
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        mask_idx = (inputs.input_ids == self.tokenizer.mask_token_id)[0].nonzero().squeeze()
        logits = outputs.logits[0, mask_idx, :]
        probs = torch.softmax(logits, dim=-1)
        
        top_k = torch.topk(probs, k=5)
        results = []
        for prob, idx in zip(top_k.values, top_k.indices):
            token = self.tokenizer.decode([idx])
            results.append((token, prob.item()))
            
        return results
