import spacy
from typing import List, Dict, Any

class OmniResult:
    def __init__(self, success: bool, value: Any = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    @classmethod
    def ok(cls, value: Any): return cls(True, value=value)
    @classmethod
    def err(cls, error: str): return cls(False, error=error)

class ClaimExtractor:
    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            import spacy.cli
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name)
            
    def extract_claims(self, text: str) -> OmniResult:
        if not text or not isinstance(text, str):
            return OmniResult.err("Invalid input text")
            
        try:
            doc = self.nlp(text)
            claims = []
            
            for sent in doc.sents:
                # Basic rule: sentences with monetary figures, ORG entities, or percentages are likely claims
                has_org = any(ent.label_ == "ORG" for ent in sent.ents)
                has_money = any(ent.label_ == "MONEY" for ent in sent.ents)
                has_percent = any(ent.label_ == "PERCENT" for ent in sent.ents)
                has_date = any(ent.label_ == "DATE" for ent in sent.ents)
                
                if (has_org and (has_money or has_percent)) or (has_date and has_money):
                    claims.append({
                        "text": sent.text.strip(),
                        "entities": [{"text": ent.text, "label": ent.label_} for ent in sent.ents],
                        "confidence": 0.85 # Heuristic confidence
                    })
                    
            return OmniResult.ok(claims)
        except Exception as e:
            return OmniResult.err(f"Extraction failed: {str(e)}")
