from typing import Dict, Any

class FullStackTransformerClient:
    def send_request(self, payload: str) -> Dict[str, Any]:
        try:
            return {"status": "success", "response": "mock_response"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
