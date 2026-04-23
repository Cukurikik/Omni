"""OmniGlossaryTrieEngine for efficient term prefix-searching."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end_of_word = False
        self.definition = None

class OmniGlossaryTrieEngine(OmniBaseEngine):
    """Production-grade Omni Glossary Trie Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, definition: str) -> Result[bool, str]:
        """Inserts a word into the Trie."""
        try:
            node = self.root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_end_of_word = True
            node.definition = definition
            return Result.ok(True)
        except Exception as e:
            return Result.fail(str(e))

    def search_exact(self, word: str) -> Result[Dict[str, Any], str]:
        """Searches for an exact word match."""
        try:
            node = self.root
            for char in word:
                if char not in node.children:
                    return Result.ok({"found": False, "definition": None})
                node = node.children[char]
                
            if node.is_end_of_word:
                return Result.ok({"found": True, "definition": node.definition})
            return Result.ok({"found": False, "definition": None})
            
        except Exception as e:
            return Result.fail(str(e))

    def get_words_with_prefix(self, prefix: str) -> Result[List[str], str]:
        """Returns all words with the given prefix."""
        try:
            node = self.root
            for char in prefix:
                if char not in node.children:
                    return Result.ok([])
                node = node.children[char]

            results = []
            self._dfs(node, prefix, results)
            return Result.ok(results)
            
        except Exception as e:
            return Result.fail(str(e))

    def _dfs(self, node: TrieNode, path: str, results: List[str]):
        if node.is_end_of_word:
            results.append(path)
        
        # Sort keys to make DFS deterministic
        for char in sorted(node.children.keys()):
            self._dfs(node.children[char], path + char, results)

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniGlossaryTrieEngine",
            "status": "operational",
            "complexity": "O(N) for insertion/search"
        }
