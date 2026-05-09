"""
@omni-layer Compute | @omni-source tatsu-lab/stanford_alpaca
@omni-description Instruction tuning data pipeline: template formatting, quality
filtering, and instruction-response pair validation.
@omni-lang Python | @omni-batch 16 | @omni-semester 16
"""
from typing import List, Dict, Optional

class OmniResult:
    __slots__ = ("data","error")
    def __init__(self, data=None, error=None): self.data, self.error = data, error
    def is_ok(self): return self.error is None

ALPACA_TEMPLATE = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:\n{response}"
ALPACA_INPUT_TEMPLATE = "Below is an instruction that describes a task, paired with further context. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{response}"

class OmniInstructionPipeline:
    def __init__(self, max_len=2048, min_response_len=10):
        self.max_len = max_len; self.min_response_len = min_response_len

    def format_example(self, instruction: str, response: str, context: Optional[str] = None) -> OmniResult:
        try:
            if not instruction or not response: return OmniResult(error=Exception("Empty fields"))
            if context:
                text = ALPACA_INPUT_TEMPLATE.format(instruction=instruction, input=context, response=response)
            else:
                text = ALPACA_TEMPLATE.format(instruction=instruction, response=response)
            if len(text) > self.max_len:
                text = text[:self.max_len]
            return OmniResult(data={"formatted": text, "length": len(text), "has_input": context is not None})
        except Exception as e: return OmniResult(error=e)

    def validate_batch(self, examples: List[Dict]) -> OmniResult:
        try:
            valid = []; rejected = []
            for ex in examples:
                inst = ex.get("instruction", ""); resp = ex.get("output", "")
                if not inst: rejected.append({"reason": "no_instruction", "idx": len(valid)+len(rejected)}); continue
                if len(resp) < self.min_response_len: rejected.append({"reason": "short_response", "idx": len(valid)+len(rejected)}); continue
                valid.append(ex)
            return OmniResult(data={"valid": len(valid), "rejected": len(rejected), "rejection_reasons": rejected[:5], "acceptance_rate": len(valid)/max(len(examples),1)})
        except Exception as e: return OmniResult(error=e)

    def compute_statistics(self, examples: List[Dict]) -> OmniResult:
        try:
            inst_lens = [len(ex.get("instruction","")) for ex in examples]
            resp_lens = [len(ex.get("output","")) for ex in examples]
            return OmniResult(data={"n_examples": len(examples), "avg_instruction_len": sum(inst_lens)/max(len(inst_lens),1), "avg_response_len": sum(resp_lens)/max(len(resp_lens),1), "max_instruction": max(inst_lens) if inst_lens else 0, "max_response": max(resp_lens) if resp_lens else 0})
        except Exception as e: return OmniResult(error=e)
