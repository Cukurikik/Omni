from typing import Dict, Any

class TextCleaner:
    def clean(self, raw_text: str) -> Dict[str, Any]:
        try:
            cleaned = raw_text.strip().replace("\n", " ")
            return {"status": "success", "cleaned_text": cleaned}
        except Exception as e:
            return {"status": "error", "message": str(e)}
