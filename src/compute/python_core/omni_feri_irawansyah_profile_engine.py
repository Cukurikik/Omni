from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniFeriIrawansyahProfileEngine:
    """
    Engine to model simple CSS/HTML specificity resolution logic deterministically.
    """
    def __init__(self) -> None:
        self.rules: Dict[str, int] = {}

    def add_stylesheet_rule(self, selector: str, specificity: int) -> Result[bool, str]:
        """Perform add stylesheet rule computation.

            Args:
                    selector: str
                    specificity: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not selector:
            return Err("Invalid selector")
        if specificity < 0:
            return Err("Specificity cannot be negative")
            
        self.rules[selector] = specificity
        return Ok(True)

    def match_element(self, matched_selectors: list) -> Result[int, str]:
        """Perform match element computation.

            Args:
                    matched_selectors: list

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not matched_selectors:
            return Err("No selector provided")
            
        max_spec = -1
        for sel in matched_selectors:
            if sel in self.rules:
                max_spec = max(max_spec, self.rules[sel])
                
        if max_spec == -1:
            return Err("No matching rules found in stylesheet")
            
        return Ok(max_spec)

    def calculate_layout_shifts(self, viewports: list) -> Result[float, str]:
        """Perform calculate layout shifts computation.

            Args:
                    viewports: list

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not viewports:
            return Err("Empty viewport matrices")
            
        shifts = 0.0
        for i in range(1, len(viewports)):
            diff = abs(viewports[i] - viewports[i-1])
            shifts += diff
            
        return Ok(shifts)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "rule_count": len(self.rules),
            "engine": "OmniFeriIrawansyahProfileEngine"
        }
