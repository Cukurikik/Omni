import logging
import uuid
import re
from src.compute.python_core.omni_base_engine import Result, Ok, Err

logger = logging.getLogger(__name__)

class OmniMhMakefileEngine:
    """
    OMNI Semester 10 Batch 31 - Production Makefile Help Generator
    Parses Makefiles to dynamically generate comprehensive documentation.
    Uses regex AST tree derivations ensuring complete deterministic output.
    """
    def __init__(self, config=None):
        self._config = config or {}
        self._system_id = str(uuid.uuid4())
        self._is_operational = True
        self._parsed_makefiles = 0

    def parse_makefile(self, makefile_content: str) -> dict:
        """
        Extracts targets and their adjoining comments.
        Target format: `target: ## Description`
        """
        if not self._is_operational:
            return {"status": "error", "error": "Parser engine offline."}
            
        if not makefile_content.strip():
            return {"status": "error", "error": "Makefile content is empty."}
            
        targets = {}
        # Strict parsing algorithm for standard makefile help conventions
        pattern = re.compile(r'^([a-zA-Z0-9_\-]+)\s*:[^#]*##\s*(.*)$')
        
        lines = makefile_content.split('\n')
        for line in lines:
            match = pattern.match(line.strip())
            if match:
                target_name = match.group(1)
                description = match.group(2).strip()
                targets[target_name] = description
                
        self._parsed_makefiles += 1
        
        # Sort targets alphabetically for deterministic OMNI behavior
        sorted_targets = {k: targets[k] for k in sorted(targets)}
        
        return {"status": "ok", "value": {"targets_found": len(sorted_targets), "docs": sorted_targets}}

    def diagnostics(self) -> dict:
        return {
            "engine": "OmniMhMakefileEngine",
            "version": "3.1.0",
            "status": "operational" if self._is_operational else "offline",
            "system_id": self._system_id,
            "capabilities": [
                "regex_makefile_ast_parsing",
                "deterministic_help_generation",
                "target_extraction"
            ],
            "metrics": {
                "parsed_makefiles": self._parsed_makefiles
            }
        }
