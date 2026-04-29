from typing import List
from omni.core import Result, Ok, Err

class EmbeddingStore:
    def __init__(self):
        self._store = {}

    def add_embeddings(self, ids: List[str], embeddings: List[List[float]]) -> Result[bool, ValueError]:
        if len(ids) != len(embeddings):
            return Err(ValueError("Length mismatch between ids and embeddings"))
        for id_, emb in zip(ids, embeddings):
            self._store[id_] = emb
        return Ok(True)
