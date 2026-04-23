import datetime
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniPromptTokenBudgetEngine:
    """
    OmniPromptTokenBudgetEngine
    Batch: 26 (Semester 10)
    Source: DarkCaster/Perpetual
    
    A zero-mock deterministic context window budgeting engine. 
    Secures reserve margins (e.g. system prompts, generation headroom)
    and distributes remaining tokens across multiple knowledge representations
    based on priority weights using a greedy surplus distribution protocol.
    """
    
    def __init__(self, max_context_window: int, reserve_system: int, reserve_completion: int):
        self.max_context_window = max_context_window
        self.reserve_system = reserve_system
        self.reserve_completion = reserve_completion

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "max_window": self.max_context_window,
            "reserves": self.reserve_system + self.reserve_completion,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def allocate_tokens(self, documents: List[Dict[str, Any]]) -> Result[Dict[str, int], Exception]:
        """
        Allocates tokens to a list of documents.
        documents should uniformly contain: {"id": str, "token_count": int, "weight": float}
        """
        try:
            if not isinstance(documents, list):
                return Err(TypeError("documents must be a list of dicts"))
                
            allocatable = self.max_context_window - self.reserve_system - self.reserve_completion
            if allocatable < 0:
                return Err(ValueError("Reserves exceed max context window"))
                
            allocations: Dict[str, int] = {}
            total_weight = sum(doc.get("weight", 0) for doc in documents)
            
            if total_weight <= 0 and len(documents) > 0:
                # Fallback to equal weighting if none are valid
                for doc in documents:
                    doc["weight"] = 1.0
                total_weight = float(len(documents))
            
            # Phase 1: Proportional naive allocation
            unmet_docs: List[Dict[str, Any]] = []
            surplus = 0
            
            for doc in documents:
                doc_id = doc.get("id")
                if doc_id is None:
                    return Err(KeyError("Document missing id"))
                
                requested = doc.get("token_count", 0)
                weight = doc.get("weight", 0.0)
                
                target_allowance = int((weight / total_weight) * allocatable) if total_weight > 0 else 0
                
                if requested <= target_allowance:
                    allocations[doc_id] = requested
                    surplus += (target_allowance - requested)
                else:
                    allocations[doc_id] = target_allowance
                    unmet_docs.append(doc)
            
            # Phase 2: Distribute surplus amongst unmet docs proportionally
            while surplus > 0 and unmet_docs:
                unmet_weight = sum(d.get("weight", 0) for d in unmet_docs)
                if unmet_weight <= 0:
                    break
                    
                next_unmet = []
                distributed = 0
                
                for doc in unmet_docs:
                    doc_id = doc["id"]
                    requested = doc["token_count"]
                    current_allocated = allocations[doc_id]
                    weight = doc["weight"]
                    
                    additional = int((weight / unmet_weight) * surplus)
                    # Force at least 1 token if there is surplus and math rounded to 0
                    if additional == 0 and surplus > 0:
                        additional = 1
                        
                    can_accept = requested - current_allocated
                    granted = min(additional, can_accept)
                    
                    allocations[doc_id] += granted
                    distributed += granted
                    
                    if allocations[doc_id] < requested:
                        next_unmet.append(doc)
                        
                if distributed == 0:
                    # Floating point/integer truncation stagnation break
                    for d in unmet_docs[0:surplus]:
                        allocations[d["id"]] += 1
                        distributed += 1
                        
                surplus -= distributed
                unmet_docs = next_unmet
                
            return Ok(allocations)
            
        except Exception as e:
            return Err(e)

    def optimize_payload(self, documents: List[Dict[str, Any]]) -> Result[Dict[str, Any], Exception]:
        """
        Coordinates full context allocation, specifying standard drops, truncations, and usage margins.
        """
        try:
            alloc_res = self.allocate_tokens(documents)
            if not alloc_res.is_ok():
                return Err(alloc_res.unwrap_err())
                
            allocations = alloc_res.unwrap()
            
            payload = {
                "system_prompt_reserve": self.reserve_system,
                "completion_margin": self.reserve_completion,
                "document_budgets": allocations,
                "total_consumed": sum(allocations.values()) + self.reserve_system + self.reserve_completion,
                "dropped_documents": [doc["id"] for doc in documents if allocations.get(doc["id"], 0) == 0 and doc.get("token_count", 0) > 0]
            }
            return Ok(payload)
        except Exception as e:
            return Err(e)
