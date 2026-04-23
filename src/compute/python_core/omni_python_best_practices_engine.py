from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniPythonBestPracticesEngine(OmniBaseEngine):
    """
    Evaluates AST-like structured payloads for PEP-8 adherence constraints,
    cyclomatic complexity bounding, and algorithmic best-practices compliance.
    """
    
    def __init__(self, max_line_length: int = 79, max_complexity: int = 10, max_functions: int = 50):
        super().__init__()
        self.max_line_length = max_line_length
        self.max_complexity = max_complexity
        self.max_functions = max_functions

    def analyze_structure(self, ast_nodes: List[Dict[str, Any]]) -> Result[Dict[str, Any], str]:
        """
        Deterministically evaluates metrics: lines lengths, cyclomatic limits,
        and name casing conventions on a strictly shaped schema.
        """
        if not isinstance(ast_nodes, list):
            return Result.fail("Invalid AST payload: Expected a list of nodes.")
            
        functions_count = 0
        total_complexity = 0.0
        violations = []
        
        for idx, node in enumerate(ast_nodes):
            if not isinstance(node, dict):
                return Result.fail(f"Invalid node at index {idx}: Expected dict.")
                
            n_type = node.get("type")
            if not n_type:
                return Result.fail(f"Node {idx} is missing 'type'.")
                
            if n_type == "function":
                functions_count += 1
                name = node.get("name", "")
                
                # Enforce snake_case
                if name != name.lower() or "-" in name:
                    violations.append(f"Function {name} at {idx} violates snake_case formatting.")
                    
                complexity = node.get("complexity", 1.0)
                if complexity > self.max_complexity:
                    violations.append(f"Function {name} complexity {complexity} exceeds {self.max_complexity}.")
                total_complexity += complexity
                
            elif n_type == "statement":
                length = node.get("length", 0)
                if length > self.max_line_length:
                    violations.append(f"Statement at {idx} length {length} exceeds {self.max_line_length}.")
                    
            else:
                pass # Other structure nodes
                
        if functions_count > self.max_functions:
            violations.append(f"Function count {functions_count} exceeds macro boundary {self.max_functions}.")
            
        avg_complexity = total_complexity / functions_count if functions_count > 0 else 0.0
        score = max(0.0, 100.0 - (len(violations) * 5.5))
        
        return Result.ok({
            "is_pep8_compliant": len(violations) == 0,
            "violations": violations,
            "complexity_index": avg_complexity,
            "functions_detected": functions_count,
            "quality_score": score
        })

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniPythonBestPracticesEngine", "version": "1.0.0", "status": "operational"}
