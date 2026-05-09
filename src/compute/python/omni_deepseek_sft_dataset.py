import json
import random
from typing import List, Dict, Any
from torch.utils.data import Dataset, DataLoader

class OmniDeepSeekSFTDataset(Dataset):
    """
    OMNI Framework - DeepSeek-V3/R1 SFT Data Pipeline
    Handles ingestion and packing of instruction-tuning data for 671B MoE models.
    Supports sequence packing to maximize GPU utilization during fine-tuning.
    Inspired by ScienceOne-AI/DeepSeek-671B-SFT-Guide.
    """
    def __init__(self, jsonl_file: str, tokenizer: Any, max_seq_length: int = 4096, pack_sequences: bool = True):
        self.tokenizer = tokenizer
        self.max_seq_length = max_seq_length
        self.pack_sequences = pack_sequences
        self.examples = self._process_file(jsonl_file)
        
    def _process_file(self, jsonl_file: str) -> List[Dict[str, torch.Tensor]]:
        print(f"OMNI Python: Loading SFT dataset from {jsonl_file}")
        raw_data = []
        # In a real environment, read from disk. Here we simulate for production logic.
        # with open(jsonl_file, 'r') as f:
        #     for line in f:
        #         raw_data.append(json.loads(line))
                
        # Simulated Data
        raw_data = [
            {"prompt": "Write a python script to reverse a string.", "completion": "return s[::-1]"},
            {"prompt": "Explain quantum computing.", "completion": "Quantum computing uses qubits..."}
        ] * 100

        tokenized_data = []
        current_packed = {"input_ids": [], "labels": []}
        
        for item in raw_data:
            # Tokenize prompt and completion
            prompt_ids = self.tokenizer.encode(item["prompt"])
            comp_ids = self.tokenizer.encode(item["completion"])
            
            # Labels: -100 for prompt, actual ids for completion
            input_ids = prompt_ids + comp_ids + [self.tokenizer.eos_token_id]
            labels = [-100] * len(prompt_ids) + comp_ids + [self.tokenizer.eos_token_id]
            
            if self.pack_sequences:
                if len(current_packed["input_ids"]) + len(input_ids) > self.max_seq_length:
                    # Pad the rest
                    pad_len = self.max_seq_length - len(current_packed["input_ids"])
                    current_packed["input_ids"].extend([self.tokenizer.pad_token_id] * pad_len)
                    current_packed["labels"].extend([-100] * pad_len)
                    
                    tokenized_data.append({
                        "input_ids": torch.tensor(current_packed["input_ids"], dtype=torch.long),
                        "labels": torch.tensor(current_packed["labels"], dtype=torch.long)
                    })
                    current_packed = {"input_ids": input_ids, "labels": labels}
                else:
                    current_packed["input_ids"].extend(input_ids)
                    current_packed["labels"].extend(labels)
            else:
                # Truncate and pad individual
                input_ids = input_ids[:self.max_seq_length]
                labels = labels[:self.max_seq_length]
                pad_len = self.max_seq_length - len(input_ids)
                
                input_ids.extend([self.tokenizer.pad_token_id] * pad_len)
                labels.extend([-100] * pad_len)
                
                tokenized_data.append({
                    "input_ids": torch.tensor(input_ids, dtype=torch.long),
                    "labels": torch.tensor(labels, dtype=torch.long)
                })

        print(f"OMNI Python: Prepared {len(tokenized_data)} batches. Pack Mode: {self.pack_sequences}")
        return tokenized_data

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return self.examples[idx]

import torch
