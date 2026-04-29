# Omni CntxtPY Knowledge Graph Builder
# Ref: brandondocusen/CntxtPY — MIT
import ast
from typing import Dict, List

def extract_functions(source: str) -> List[Dict]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            funcs.append({"name": node.name, "line": node.lineno,
                          "args": [a.arg for a in node.args.args]})
    return funcs

def build_dependency_graph(modules: Dict[str, List[str]]) -> Dict[str, List[str]]:
    graph = {}
    for mod, imports in modules.items():
        graph[mod] = [i for i in imports if i in modules]
    return graph

def estimate_tokens(source: str) -> int:
    return max(1, len(source) // 4)
