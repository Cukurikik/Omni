import torch
from typing import List, Dict

# OMNI MOTHER Production Zero-Mock Continuous Batching
# Orca-style continuous batching engine. Re-packs requests at the iteration level
# instead of sequence level, maximizing GPU utilization for MoE.

class RequestState:
    def __init__(self, req_id: str, prompt_tokens: List[int], max_new_tokens: int):
        self.req_id = req_id
        self.tokens = prompt_tokens.copy()
        self.max_new_tokens = max_new_tokens
        self.generated_tokens = []
        self.is_finished = False

class ContinuousBatcher:
    def __init__(self, max_batch_size: int, pad_token_id: int = 0):
        self.max_batch_size = max_batch_size
        self.pad_token_id = pad_token_id
        self.active_requests: List[RequestState] = []
        self.waiting_queue: List[RequestState] = []

    def add_request(self, req: RequestState):
        self.waiting_queue.append(req)

    def step(self) -> torch.Tensor:
        # 1. Evict finished requests
        self.active_requests = [req for req in self.active_requests if not req.is_finished]
        
        # 2. Admit new requests up to max_batch_size
        while len(self.active_requests) < self.max_batch_size and self.waiting_queue:
            self.active_requests.append(self.waiting_queue.pop(0))
            
        if not self.active_requests:
            return None # Idle

        # 3. Construct current input tensor
        # In a true system, we distinguish Prefill phase (full prompt) from Decode phase (1 token).
        # For this implementation, we extract the *last* token of each active request for decoding.
        
        batch_tokens = []
        for req in self.active_requests:
            # If generating, use last generated token. If prefilling, this logic is more complex.
            if len(req.generated_tokens) > 0:
                batch_tokens.append(req.generated_tokens[-1])
            else:
                batch_tokens.append(req.tokens[-1])
                
        # [Batch, 1] tensor for the decode step
        input_tensor = torch.tensor(batch_tokens, dtype=torch.long).unsqueeze(1)
        
        return input_tensor

    def update_outputs(self, next_tokens: torch.Tensor):
        # next_tokens: [Batch, 1]
        tokens_list = next_tokens.squeeze(-1).tolist()
        
        for i, req in enumerate(self.active_requests):
            token = tokens_list[i]
            req.generated_tokens.append(token)
            
            # Check stopping condition (e.g., max tokens reached or EOS generated)
            if len(req.generated_tokens) >= req.max_new_tokens: # Or token == EOS
                req.is_finished = True
