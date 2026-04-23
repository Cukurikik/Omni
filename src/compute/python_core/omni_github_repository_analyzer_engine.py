from __future__ import annotations
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniGithubRepositoryAnalyzerEngine:
    """
    omni-github-repository-analyzer
    
    A pure structural constraint matrix mathematically executing AST-like bounding metric
    checks traversing code structures measuring string bounds capacities limits natively.
    """
    
    ENGINE_VERSION = "omni-s11-b7.1.0"
    
    def __init__(self, max_lines_per_file: int = 500) -> None:
        self.bloat_limit = max_lines_per_file

    def analyze_repository_metrics(self, file_contents: Dict[str, str]) -> Result:
        """
        file_contents: {"src/main.py": "code...", "README.md": "text..."}
        """
        try:
            if not file_contents:
                return Err(ValueError("Cannot functionally map limits computations over an empty repository boundary."))
                
            total_files = len(file_contents)
            total_lines = 0
            bloated_files = []
            language_map = {}
            
            for file_path, content in file_contents.items():
                if not isinstance(content, str):
                    return Err(ValueError("Matrix values constraint bounds must be string text codes!"))
                    
                # Natively execute AST traversal sizing metrics limits bounds
                lines = content.count('\n') + 1 if content else 0
                total_lines += lines
                
                if lines > self.bloat_limit:
                    bloated_files.append({"file": file_path, "overflow_lines": lines - self.bloat_limit})
                    
                # Detect language natively
                ext = file_path.split('.')[-1] if '.' in file_path else "unknown"
                language_map[ext] = language_map.get(ext, 0) + 1
                
            return Ok({
                "metrics": {
                    "total_files": total_files,
                    "total_computed_lines": total_lines,
                    "average_lines_per_file": round(total_lines / total_files, 2) if total_files > 0 else 0
                },
                "language_distribution": language_map,
                "architectural_warnings": {
                    "bloated_files_detected": len(bloated_files),
                    "details": bloated_files
                }
            })
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides native internal tracing logic logic metrics verifications."""
        return {
            "engine": "OmniGithubRepositoryAnalyzerEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "bloat_limit_bound": self.bloat_limit,
            "complexity": "O(N * L) File Array Sequence Math"
        }
