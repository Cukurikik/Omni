"""OmniAhoCorasickEngine for fast multiple pattern matching."""
from typing import Dict, Any, List
from collections import deque
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniAhoCorasickEngine(OmniBaseEngine):
    """Production-grade Omni Aho Corasick Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self):
        self.trie = [{}]
        self.out = [[]]
        self.fail = [0]
        self.built = False

    def build(self, keywords: List[str]) -> Result[Dict[str, Any], str]:
        """Builds the Aho-Corasick automaton."""
        try:
            self.trie = [{}]
            self.out = [[]]
            self.fail = [0]
            
            # Trie insertion
            for keyword in keywords:
                curr = 0
                for c in keyword:
                    if c not in self.trie[curr]:
                        self.trie[curr][c] = len(self.trie)
                        self.trie.append({})
                        self.out.append([])
                        self.fail.append(0)
                    curr = self.trie[curr][c]
                self.out[curr].append(keyword)

            # Failure links (BFS)
            queue = deque()
            for c, nxt in self.trie[0].items():
                self.fail[nxt] = 0
                queue.append(nxt)

            while queue:
                curr = queue.popleft()
                for c, nxt in self.trie[curr].items():
                    queue.append(nxt)
                    f = self.fail[curr]
                    while f > 0 and c not in self.trie[f]:
                        f = self.fail[f]
                    if c in self.trie[f]:
                        f = self.trie[f][c]
                    self.fail[nxt] = f
                    # Merge outputs
                    self.out[nxt].extend(self.out[f])
                    
            self.built = True
            return Result.ok({"states": len(self.trie), "built": True})
        except Exception as e:
            return Result.fail(str(e))

    def search(self, text: str) -> Result[Dict[str, Any], str]:
        """Searches for multiple patterns in text."""
        try:
            if not self.built:
                return Result.fail("Automaton not built")

            curr = 0
            results = []
            for i, c in enumerate(text):
                while curr > 0 and c not in self.trie[curr]:
                    curr = self.fail[curr]
                if c in self.trie[curr]:
                    curr = self.trie[curr][c]
                else:
                    curr = 0
                
                if self.out[curr]:
                    for kw in self.out[curr]:
                        results.append({"keyword": kw, "end_index": i})
                        
            return Result.ok({"matches": results})
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniAhoCorasickEngine",
            "status": "operational" if self.built else "not_built",
            "states": len(self.trie)
        }
