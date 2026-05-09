import torch

# OMNI MOTHER: Data Collator for LLM Pretraining (Production Grade)
# Dynamically pads and masks batches for causal language modeling.

class OmniDataCollatorForCausalLM:
    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def __call__(self, features):
        input_ids = [torch.tensor(f["input_ids"]) for f in features]
        
        # Pad to max length in batch
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.pad_token_id
        )
        
        labels = input_ids.clone()
        # Ignore loss on padding
        labels[labels == self.pad_token_id] = -100 
        
        return {
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": (input_ids != self.pad_token_id).long()
        }
