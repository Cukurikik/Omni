"""
moe_continuous_batching.py — LLM Serving / Scheduler
Layer: Compute / AI — Continuous Batching

Implements iteration-level scheduling (Continuous Batching or ORCA)
specifically adapted for MoE models. Allows inserting new sequences and
evicting finished sequences at the token level rather than the sequence level,
which is critical for preventing GPU idle time during MoE generation.
"""
import torch
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SequenceRequest:
    request_id: str
    prompt_tokens: List[int]
    generated_tokens: List[int]
    max_tokens: int
    is_finished: bool = False


class MoEContinuousBatcher:
    """Manages continuous batching for MoE generation."""
    def __init__(self, max_batch_size: int, max_seq_len: int, device: str = "cuda"):
        self.max_batch_size = max_batch_size
        self.max_seq_len = max_seq_len
        self.device = torch.device(device)
        
        self.running_requests: Dict[int, SequenceRequest] = {}
        self.waiting_queue: List[SequenceRequest] = []
        
        # We assign slots (0 to max_batch_size-1) for KV cache addressing
        self.free_slots = set(range(max_batch_size))
        self.slot_to_request: Dict[int, str] = {}
        
    def add_request(self, req: SequenceRequest):
        self.waiting_queue.append(req)

    def step(self) -> Tuple[torch.Tensor, torch.Tensor, List[int]]:
        """
        Builds the next batch for the forward pass.
        Returns:
            input_tokens: (B, 1) tensor of tokens to process next
            position_ids: (B, 1) tensor of sequence positions
            slot_indices: physical KV cache slots for these sequences
        """
        self._evict_finished()
        self._schedule_new()
        
        if not self.running_requests:
            return torch.empty(0), torch.empty(0), []
            
        current_tokens = []
        positions = []
        slots = []
        
        for slot, req_id in self.slot_to_request.items():
            req = self.running_requests[req_id]
            
            # Determine the next token to process
            if not req.generated_tokens:
                # Pre-fill phase (simplified to token-by-token here for illustration,
                # real systems do chunked prefill). We'll assume the prompt is fully 
                # processed and we are emitting the first generated token.
                next_tok = req.prompt_tokens[-1]
                pos = len(req.prompt_tokens) - 1
            else:
                # Decode phase
                next_tok = req.generated_tokens[-1]
                pos = len(req.prompt_tokens) + len(req.generated_tokens) - 1
                
            current_tokens.append([next_tok])
            positions.append([pos])
            slots.append(slot)
            
        input_tensor = torch.tensor(current_tokens, dtype=torch.long, device=self.device)
        pos_tensor = torch.tensor(positions, dtype=torch.long, device=self.device)
        
        return input_tensor, pos_tensor, slots

    def update_outputs(self, output_tokens: torch.Tensor, slots: List[int]):
        """Registers the tokens predicted by the MoE forward pass."""
        outputs = output_tokens.cpu().tolist()
        
        for i, slot in enumerate(slots):
            req_id = self.slot_to_request[slot]
            req = self.running_requests[req_id]
            
            new_token = outputs[i][0]
            req.generated_tokens.append(new_token)
            
            # Check stopping conditions (e.g., EOS token = 2, or max length)
            if new_token == 2 or len(req.generated_tokens) >= req.max_tokens:
                req.is_finished = True

    def _evict_finished(self):
        """Removes finished requests and frees their KV cache slots."""
        to_remove_slots = []
        for slot, req_id in self.slot_to_request.items():
            if self.running_requests[req_id].is_finished:
                to_remove_slots.append(slot)
                
        for slot in to_remove_slots:
            req_id = self.slot_to_request.pop(slot)
            del self.running_requests[req_id]
            self.free_slots.add(slot)
            logger.debug(f"Evicted request {req_id} from slot {slot}")

    def _schedule_new(self):
        """Pulls requests from the waiting queue if slots are available."""
        while self.free_slots and self.waiting_queue:
            slot = self.free_slots.pop()
            req = self.waiting_queue.pop(0)
            
            self.running_requests[req.request_id] = req
            self.slot_to_request[slot] = req.request_id
            logger.debug(f"Scheduled request {req.request_id} into slot {slot}")
