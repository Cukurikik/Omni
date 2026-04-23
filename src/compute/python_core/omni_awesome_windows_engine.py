import re
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniAwesomeWindowsEngine:
    """
    OMNI Semester 10 Batch 32 - Awesome Windows Tool Evaluator
    Examines 'awesome list' markdown payloads deterministically to construct
    software registry databases for offline usage.
    """
    def __init__(self, config=None):
        self._config = config or {}
        self._is_operational = True
        self._engine_id = "awesome-windows-parser"
        self._entry_regex = re.compile(r"^\*\s+\[([^\]]+)\]\(([^)]+)\)\s+-\s+(.+)$")

    def parse_tools_markdown(self, markdown_content: str) -> dict:
        """
        Parses Markdown formatted like "* [Name](URL) - Description"
        Monadic return.
        """
        if not self._is_operational:
            return {"status": "error", "error": "Engine offline."}
            
        tools_registry = []
        lines = markdown_content.splitlines()
        
        for line in lines:
            line = line.strip()
            match = self._entry_regex.match(line)
            if match:
                name, url, desc = match.groups()
                tools_registry.append({
                    "name": name.strip(),
                    "url": url.strip(),
                    "description": desc.strip()
                })
                
        # Hash deterministic sequence calculation to track version changes without mock randomness
        registry_hash = sum([len(t["name"]) * i for i, t in enumerate(tools_registry)])
                
        return {
            "status": "ok",
            "value": {
                "extracted_count": len(tools_registry),
                "registry_hash_signature": registry_hash,
                "registry": tools_registry
            }
        }

    def diagnostics(self) -> dict:
        return {
            "engine": "OmniAwesomeWindowsEngine",
            "version": "3.2.0",
            "status": "operational" if self._is_operational else "offline",
            "system_id": self._engine_id,
            "capabilities": [
                "markdown_ast_parser",
                "registry_signature_hashing",
                "deterministic_payload_extraction"
            ]
        }
