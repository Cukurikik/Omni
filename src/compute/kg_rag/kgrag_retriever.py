# KG_RAG Retriever
from typing import Optional, Generic, TypeVar, List, Dict

T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class KGRAGRetriever:
    def __init__(self):
        self.kg_index = {}

    def add_triplet(self, sub: str, pred: str, obj: str) -> OmniResult[bool, str]:
        if not sub or not obj: return OmniResult(error="Empty node")
        if sub not in self.kg_index: self.kg_index[sub] = []
        self.kg_index[sub].append((pred, obj))
        return OmniResult(value=True)

    def retrieve_context(self, entity: str, hop: int = 1) -> OmniResult[List[str], str]:
        if hop < 1: return OmniResult(error="Hop must be >= 1")
        if entity not in self.kg_index: return OmniResult(value=[])
        
        context = []
        for pred, obj in self.kg_index[entity]:
            context.append(f"{entity} {pred} {obj}")
        return OmniResult(value=context)
