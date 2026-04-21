"""
+============================================================================+
|  OMNI RIG ENGINE (TRUE LLM AGENT)                                          |
|  Meta-functionalized from: 0xPlaygrounds/rig                               |
|  Domain Layer: OMNI_AI / Compute                                           |
|  Purpose: Hard-coded production execution of real LLM HTTP network calls.  |
|  Constraints: ZERO MOCKS. Real network resolution.                         |
|  License: OMNI-Enterprise                                                  |
+============================================================================+
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import urllib.request
import urllib.error
import urllib.parse
import json

T = Any
E = Exception

@dataclass
class Result:
    is_ok: bool
    value: Optional[T] = None
    error: Optional[E] = None

    @staticmethod
    def Ok(value: T) -> 'Result':
        return Result(is_ok=True, value=value)

    @staticmethod
    def Err(error: E) -> 'Result':
        return Result(is_ok=False, error=error)

    def unwrap(self) -> T:
        if not self.is_ok:
            raise self.error or Exception("Unwrapped an Err result")
        return self.value

@dataclass
class RigMessage:
    role: str
    content: str

class OmniRigEngine:
    """
    Production-grade LLM Agent wrapper based on 'rig' philosophy.
    Performs ACTUAL network requests to standard OpenAI-compatible endpoints.
    Does NOT mock answers.
    """
    
    ENGINE_VERSION = "2.0.0-PROD"

    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1", model: str = "gpt-4o"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._memory: List[RigMessage] = []

    def set_system_prompt(self, prompt: str):
        """Clears memory and sets the initial system prompt."""
        self._memory = [RigMessage(role="system", content=prompt)]

    def _execute_real_http_completion(self, messages: List[Dict[str, str]]) -> Result:
        """Internal: Safely runs a real HTTP request returning raw JSON as Result."""
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": 0.5
        }).encode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = response.getcode()
                if status_code == 200:
                    data = response.read().decode('utf-8')
                    return Result.Ok(json.loads(data))
                else:
                    return Result.Err(Exception(f"HTTP Return {status_code}"))
        except urllib.error.HTTPError as e:
            return Result.Err(Exception(f"API Error ({e.code}): {e.read().decode('utf-8')}"))
        except Exception as e:
            return Result.Err(e)

    def ask(self, query: str) -> Result:
        """
        Appends user query to memory and performs a live network call.
        """
        # Append User
        self._memory.append(RigMessage(role="user", content=query))
        
        # Serialize format
        raw_msgs = [{"role": m.role, "content": m.content} for m in self._memory]
        
        # Real Network Resolution
        res = self._execute_real_http_completion(raw_msgs)
        
        if not res.is_ok:
            # Drop failed message from memory to avoid corruption
            self._memory.pop()
            return res
            
        try:
            response_json = res.unwrap()
            assistant_content = response_json["choices"][0]["message"]["content"]
            
            # Append Assistant
            self._memory.append(RigMessage(role="assistant", content=assistant_content))
            return Result.Ok({"response": assistant_content, "raw_data": response_json})
        except Exception as e:
            return Result.Err(Exception(f"Failed to parse provider response: {e}"))

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Framework standard diagnostics method."""
        return {
            "engine": "OmniRigEngine",
            "version": self.ENGINE_VERSION,
            "model_configured": self.model,
            "messages_in_memory": len(self._memory)
        }

# ============================================================================
# Engine Self-Test
# ============================================================================
def _run_self_test():
    # Production note: Without a real valid API key here,
    # the network request should cleanly and expectedly fail with a 401 via Result.Err.
    engine = OmniRigEngine(api_key="TEST_INVALID_KEY")
    engine.set_system_prompt("You are a real agent testing network failures.")
    
    # Send actual live request
    res = engine.ask("Ping")
    
    # It must fail because of the invalid key, NOT crash.
    assert not res.is_ok
    assert "401" in str(res.error) or "API Error" in str(res.error)
    
    diag = engine.diagnostics()
    assert diag["messages_in_memory"] == 1 # Has the system prompt, user prompt was popped on error.
    print("OmniRigEngine: Production unmocked tests passed (Handled 401 correctly).")

if __name__ == "__main__":
    _run_self_test()
