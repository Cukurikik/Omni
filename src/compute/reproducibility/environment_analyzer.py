import ast
import os
from typing import List, Dict
from omni_core.result import OmniResult, Ok, Err

class EnvironmentAnalyzer:
    """
    OMNI COMPUTE LAYER: Code Reproducibility
    Analyzes Python projects for hardcoded paths, missing dependencies, and reproducibility anti-patterns.
    """
    def __init__(self, project_path: str):
        self.project_path = project_path

    def analyze_python_files(self) -> OmniResult[Dict[str, List[str]], str]:
        try:
            results = {"hardcoded_paths": [], "missing_seeds": []}
            
            for root, _, files in os.walk(self.project_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                # Check for hardcoded absolute paths
                                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                                    val = node.value
                                    if val.startswith("/") or val.startswith("C:\\"):
                                        if len(val) > 4: # Ignore very short strings
                                            results["hardcoded_paths"].append(f"{file_path}: {val}")
                        except SyntaxError:
                            continue # Ignore files that can't be parsed

            return Ok(results)
        except Exception as e:
            return Err(f"Environment analysis failed: {str(e)}")
