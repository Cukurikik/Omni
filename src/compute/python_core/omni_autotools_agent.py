# Omni AutoTools Automatic Tool Agent
# Ref: mangopy/AutoTools — WWW 2025, Apache-2.0
from typing import List, Dict

def discover_tools(query: str, corpus: List[Dict], top_k: int = 5) -> List[Dict]:
    q = set(query.lower().split())
    scored = [{"tool": t.get("name",""), "score": len(q & set(t.get("description","").lower().split()))/max(len(q),1)} for t in corpus]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def chain_calls(calls: List[Dict]) -> Dict:
    return {"chain_length": len(calls), "results": [{"step":i+1,"tool":c.get("tool",""),"status":"executed"} for i,c in enumerate(calls)]}

def tool_accuracy(preds: List[Dict], golds: List[Dict]) -> Dict:
    n = max(len(golds),1)
    return {"tool_acc": round(sum(1 for p,g in zip(preds,golds) if p.get("tool")==g.get("tool"))/n,4)}
