"""OmniW3appdevKodeposGeoEngine — Hierarchical Geographic Code Validation.

Inspired by w3appdev/kodepos: a database of Indonesian administrative
regions (province → regency → district → village → postal code).

Algorithmic Primitive:
    Validate hierarchical geographic code chains using a trie-like
    containment structure. Given a chain [province, regency, district,
    village], verify that each level is a valid child of the previous level.
    Also supports postal-code-to-region reverse lookup validation.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniW3appdevKodeposGeoEngine:
    """Production-grade hierarchical geographic code validator."""

    HIERARCHY_LEVELS = ["province", "regency", "district", "village"]

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniW3appdevKodeposGeoEngine",
            "version": "1.0.0",
            "primitive": "trie_hierarchical_geo_code_validation",
            "monadic_enforcement": True,
            "source_repo": "w3appdev/kodepos",
        }

    @staticmethod
    def validate_hierarchy(tree: dict, chain: list[str]) -> Result:
        """Validate a hierarchical geographic code chain against a trie.

        Args:
            tree: Nested dict representing the administrative hierarchy.
                  Example: {"JAWA_BARAT": {"BANDUNG": {"COBLONG": {}}}}
            chain: List of region names from top to bottom.
                   Example: ["JAWA_BARAT", "BANDUNG", "COBLONG"]

        Returns:
            Result[bool, Exception]: True if the chain is valid, Err otherwise.
        """
        if not isinstance(tree, dict):
            return Err(Exception("tree must be a dict representing the geo hierarchy"))
        if not isinstance(chain, list) or len(chain) == 0:
            return Err(Exception("chain must be a non-empty list of region names"))

        current = tree
        for i, region in enumerate(chain):
            if not isinstance(current, dict):
                level = OmniW3appdevKodeposGeoEngine.HIERARCHY_LEVELS[i] if i < 4 else f"level-{i}"
                return Err(Exception(
                    f"Hierarchy terminates before reaching '{region}' at {level}"
                ))
            if region not in current:
                level = OmniW3appdevKodeposGeoEngine.HIERARCHY_LEVELS[i] if i < 4 else f"level-{i}"
                return Err(Exception(
                    f"Unknown {level} '{region}'. Valid options: {list(current.keys())}"
                ))
            current = current[region]

        return Ok(True)

    @staticmethod
    def validate_postal_code(
        postal_code: str,
        postal_map: dict[str, list[str]],
    ) -> Result:
        """Validate that a postal code exists and return its regions.

        Args:
            postal_code: The postal code string (e.g. "40132").
            postal_map: dict mapping postal_code -> list of region names.

        Returns:
            Result[list[str], Exception]: List of regions for this postal code.
        """
        if not postal_code or not isinstance(postal_code, str):
            return Err(Exception("postal_code must be a non-empty string"))
        if not isinstance(postal_map, dict):
            return Err(Exception("postal_map must be a dict[str, list[str]]"))

        if postal_code not in postal_map:
            return Err(Exception(f"Postal code '{postal_code}' not found in registry"))

        return Ok(postal_map[postal_code])

    @staticmethod
    def compute_depth(tree: dict) -> Result:
        """Compute the maximum depth of a geographic hierarchy tree.

        Args:
            tree: Nested dict representing the hierarchy.

        Returns:
            Result[int, Exception]: Maximum depth of the tree.
        """
        if not isinstance(tree, dict):
            return Err(Exception("tree must be a dict"))

        if not tree:
            return Ok(0)

        max_child_depth = 0
        for child in tree.values():
            if isinstance(child, dict):
                child_result = OmniW3appdevKodeposGeoEngine.compute_depth(child)
                if not child_result.is_ok():
                    return child_result
                max_child_depth = max(max_child_depth, child_result.unwrap())

        return Ok(1 + max_child_depth)
