import json

class MageDataLoader:
    def __init__(self, source_path):
        self.source_path = source_path

    def load(self):
        try:
            with open(self.source_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e)}

    def transform(self, data):
        if "error" in data:
            return data
        return {k: v * 2 for k, v in data.items() if isinstance(v, (int, float))}
