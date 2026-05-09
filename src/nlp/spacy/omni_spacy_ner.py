# OMNI Framework - spaCy Named Entity Recognition (Python)
# Fallback or pre-processing NLP pipeline to extract entities before feeding to LLM

import spacy
import json

class OmniSpacyNER:
    def __init__(self, model_name="en_core_web_sm"):
        """
        Initializes the spaCy NER pipeline.
        Ensure model is downloaded: python -m spacy download en_core_web_sm
        """
        try:
            self.nlp = spacy.load(model_name)
            print(f"OMNI Python: Loaded spaCy model '{model_name}'")
        except OSError:
            print(f"OMNI Python: Error - spaCy model '{model_name}' not found.")
            self.nlp = None

    def extract_entities(self, text: str) -> str:
        """
        Extracts named entities from text and returns them as a JSON string.
        """
        if not self.nlp:
            return json.dumps({"error": "Model not loaded"})

        doc = self.nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        
        return json.dumps({"entities": entities})

# Example Usage:
# if __name__ == "__main__":
#     ner = OmniSpacyNER()
#     result = ner.extract_entities("Apple is looking at buying U.K. startup for $1 billion")
#     print(result)
