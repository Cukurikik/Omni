"""OmniTrieEngine — Production-grade trie (prefix tree) data structure.

Implements trie with insert, search, prefix matching, autocomplete,
and word count operations. Used for string indexing and lookup.
"""
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class _TrieNode:
    __slots__ = ('children', 'is_end', 'count')

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.count = 0


class OmniTrieEngine:
    """Production engine for Trie (prefix tree) operations."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self):
        self._root = _TrieNode()
        self._word_count = 0

    def insert(self, word: str) -> Result:
        """Perform insert computation.

            Args:
                    word: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if not word:
                return Err(ValueError("Word must be non-empty."))
            node = self._root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = _TrieNode()
                node = node.children[ch]
                node.count += 1
            if not node.is_end:
                node.is_end = True
                self._word_count += 1
                return Ok({"inserted": True, "word": word, "total_words": self._word_count})
            return Ok({"inserted": False, "word": word, "already_exists": True, "total_words": self._word_count})
        except Exception as e:
            return Err(e)

    def search(self, word: str) -> Result:
        """Perform search computation.

            Args:
                    word: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            node = self._root
            for ch in word:
                if ch not in node.children:
                    return Ok({"found": False, "word": word})
                node = node.children[ch]
            return Ok({"found": node.is_end, "word": word})
        except Exception as e:
            return Err(e)

    def starts_with(self, prefix: str) -> Result:
        """Perform starts with computation.

            Args:
                    prefix: str

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            node = self._root
            for ch in prefix:
                if ch not in node.children:
                    return Ok({"has_prefix": False, "prefix": prefix, "count": 0})
                node = node.children[ch]
            return Ok({"has_prefix": True, "prefix": prefix, "count": node.count})
        except Exception as e:
            return Err(e)

    def autocomplete(self, prefix: str, max_results: int = 10) -> Result:
        """Perform autocomplete computation.

            Args:
                    prefix: str
                    max_results: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            node = self._root
            for ch in prefix:
                if ch not in node.children:
                    return Ok({"prefix": prefix, "suggestions": [], "count": 0})
                node = node.children[ch]
            suggestions = []
            self._dfs(node, prefix, suggestions, max_results)
            return Ok({"prefix": prefix, "suggestions": suggestions, "count": len(suggestions)})
        except Exception as e:
            return Err(e)

    def _dfs(self, node, current, results, max_r):
        if len(results) >= max_r:
            return
        if node.is_end:
            results.append(current)
        for ch in sorted(node.children.keys()):
            self._dfs(node.children[ch], current + ch, results, max_r)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniTrieEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "word_count": self._word_count}
