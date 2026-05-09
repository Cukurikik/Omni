"""
OMNI Transformer — Data Pipeline for Tokenization and Batching
Production data loading with dynamic padding, bucketing, and streaming.
Learned from: gszfwsb/Data-Whisperer, mts-ai/OpenAutoNLU
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any, Optional, Callable
import torch
from torch.utils.data import Dataset, DataLoader

logger = logging.getLogger(__name__)


class TextDataset(Dataset):
    """Generic text dataset with lazy tokenization."""
    def __init__(self, texts: List[str], labels: Optional[List[int]] = None,
                 tokenize_fn: Optional[Callable] = None, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenize_fn = tokenize_fn
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        text = self.texts[idx]
        if self.tokenize_fn:
            encoded = self.tokenize_fn(text, max_length=self.max_length, truncation=True, padding=False)
        else:
            # Simple character-level fallback
            encoded = {"input_ids": [ord(c) % 30000 for c in text[:self.max_length]]}

        item = {"input_ids": torch.tensor(encoded["input_ids"], dtype=torch.long)}
        if "attention_mask" in encoded:
            item["attention_mask"] = torch.tensor(encoded["attention_mask"], dtype=torch.long)
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item


class CausalLMDataset(Dataset):
    """Dataset for causal language modeling (input_ids == labels shifted by 1)."""
    def __init__(self, token_ids: List[List[int]], block_size: int = 1024):
        self.examples = []
        for ids in token_ids:
            for i in range(0, len(ids) - block_size, block_size):
                chunk = ids[i:i + block_size + 1]
                if len(chunk) == block_size + 1:
                    self.examples.append(chunk)

    def __len__(self) -> int:
        return len(self.examples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        chunk = self.examples[idx]
        return {
            "input_ids": torch.tensor(chunk[:-1], dtype=torch.long),
            "labels": torch.tensor(chunk[1:], dtype=torch.long),
        }


class DynamicPaddingCollator:
    """Collate function with dynamic padding to longest in batch."""
    def __init__(self, pad_token_id: int = 0, label_pad_id: int = -100):
        self.pad_token_id = pad_token_id
        self.label_pad_id = label_pad_id

    def __call__(self, batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        max_len = max(b["input_ids"].size(0) for b in batch)
        result = {}

        for key in batch[0].keys():
            pad_id = self.label_pad_id if key == "labels" else self.pad_token_id
            tensors = []
            for b in batch:
                t = b[key]
                pad_size = max_len - t.size(0)
                if pad_size > 0:
                    t = torch.nn.functional.pad(t, (0, pad_size), value=pad_id)
                tensors.append(t)
            result[key] = torch.stack(tensors)

        if "attention_mask" not in result:
            result["attention_mask"] = (result["input_ids"] != self.pad_token_id).long()

        return result


class BucketBatchSampler:
    """Sampler that groups sequences of similar length for efficient batching."""
    def __init__(self, lengths: List[int], batch_size: int, shuffle: bool = True):
        self.batch_size = batch_size
        sorted_indices = sorted(range(len(lengths)), key=lambda i: lengths[i])

        self.batches = []
        for i in range(0, len(sorted_indices), batch_size):
            batch = sorted_indices[i:i + batch_size]
            if len(batch) == batch_size:
                self.batches.append(batch)

        if shuffle:
            import random
            random.shuffle(self.batches)

    def __iter__(self):
        return iter(self.batches)

    def __len__(self) -> int:
        return len(self.batches)


def create_dataloader(
    dataset: Dataset, batch_size: int = 32, pad_token_id: int = 0,
    num_workers: int = 4, shuffle: bool = True,
) -> DataLoader:
    """Factory function to create production dataloader."""
    collator = DynamicPaddingCollator(pad_token_id=pad_token_id)
    return DataLoader(
        dataset, batch_size=batch_size, shuffle=shuffle,
        collate_fn=collator, num_workers=num_workers,
        pin_memory=torch.cuda.is_available(), drop_last=False,
    )
