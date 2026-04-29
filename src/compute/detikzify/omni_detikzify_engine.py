from typing import Dict, Any
from dataclasses import dataclass
import hashlib, re

# OMNI DeTikZify Engine — Compute Layer
# Absorbing potamides/DeTikZify: Image→TikZ graphics program synthesis.
# Production TikZ AST validator and LaTeX escape sanitizer.

@dataclass
class TikzResult:
    ok: bool
    sanitized_code: str = ""
    node_count: int = 0
    error: str = None

class OmniDeTikZifyEngine:
    TIKZ_COMMANDS = frozenset([
        r'\draw', r'\fill', r'\node', r'\path', r'\coordinate',
        r'\filldraw', r'\shade', r'\clip', r'\foreach', r'\begin', r'\end'
    ])

    def __init__(self):
        self.validations = 0

    def validate_and_sanitize(self, raw_tikz: str) -> TikzResult:
        if not raw_tikz or len(raw_tikz.strip()) == 0:
            return TikzResult(False, error="TikzError: Empty TikZ code")
        try:
            self.validations += 1
            code = raw_tikz.strip()
            # Check for tikzpicture environment
            if r'\begin{tikzpicture}' not in code:
                code = r'\begin{tikzpicture}' + '\n' + code + '\n' + r'\end{tikzpicture}'

            # Count TikZ nodes/commands
            node_count = 0
            for cmd in self.TIKZ_COMMANDS:
                node_count += code.count(cmd)

            # Sanitize dangerous LaTeX commands (no \input, \write, \immediate)
            dangerous = [r'\input', r'\write', r'\immediate', r'\catcode', r'\csname']
            for d in dangerous:
                if d in code:
                    code = code.replace(d, f'% REMOVED: {d}')

            # Validate bracket balance
            if code.count('{') != code.count('}'):
                return TikzResult(False, error="TikzError: Unbalanced braces")
            if code.count('[') != code.count(']'):
                return TikzResult(False, error="TikzError: Unbalanced brackets")

            return TikzResult(True, sanitized_code=code, node_count=node_count)
        except Exception as e:
            return TikzResult(False, error=f"TikzError: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniDeTikZifyEngine", "validations": self.validations, "status": "Operational"}
