# OMNI Compute Layer - LlamaIndex Graph Router
class LlamaIndexError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        
    def is_ok(self):
        return self.error is None

def route_query_to_index(query: str, available_indices: dict) -> Result:
    """Routes queries to the optimal vector or keyword index using LlamaIndex logic."""
    try:
        if not query or not available_indices:
            return Result(error=LlamaIndexError("Query and indices required"))
            
        selected_index = None
        if "summary" in query.lower():
            selected_index = available_indices.get("document_summary")
        else:
            selected_index = available_indices.get("vector_store")
            
        return Result(value={"routed_target": selected_index, "query": query})
    except Exception as e:
        return Result(error=LlamaIndexError(f"Routing failed: {str(e)}"))
