# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# FastAPI Async Router (OMNI Zero-Mock Implementation)
# Implements Trie-based Path Resolution for quick HTTP routing.

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

@dataclass
class Result:
    value: Optional[str] # handler UUID
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: str) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.handler_id: Optional[str] = None
        self.is_param: bool = False

class FastAPIRouterCore:
    def __init__(self):
        self.root = TrieNode()

    def add_route(self, path: str, handler_id: str) -> None:
        parts = path.strip('/').split('/')
        current = self.root
        for p in parts:
            if not p: continue
            
            is_param = p.startswith('{') and p.endswith('}')
            key = '*' if is_param else p
            
            if key not in current.children:
                node = TrieNode()
                node.is_param = is_param
                current.children[key] = node
                
            current = current.children[key]
        current.handler_id = handler_id

    def resolve_route(self, path: str) -> Result:
        parts = path.strip('/').split('/')
        current = self.root
        
        for p in parts:
            if not p: continue
            
            if p in current.children:
                current = current.children[p]
            elif '*' in current.children:
                current = current.children['*']
            else:
                return Result.err(f"404 Not Found: Segment '{p}' has no match.")
                
        if current.handler_id:
             return Result.ok(current.handler_id)
        return Result.err("404 Not Found: Incomplete path match.")
