"""
omni_data_collator.py — Dynamic Batching & Collation
Inspired by: HuggingFace DataCollator patterns for OMNI training
Layer: Compute / AI

Production data collation with dynamic padding, sequence bucketing,
MLM masking, and multi-modal batch assembly.
"""

import torch
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
import math


@dataclass
class CollatorConfig:
    pad_token_id: int = 0
    mask_token_id: int = 4
    mlm_probability: float = 0.15
    max_length: Optional[int] = None
    pad_to_multiple_of: int = 8
    label_pad_id: int = -100
    dynamic_padding: bool = True


class OmniDataCollator:
    """Dynamic batch collator with padding and masking.

    Handles variable-length sequences with efficient padding,
    optional MLM masking, and multi-modal input assembly.
    """

    def __init__(self, config: CollatorConfig = CollatorConfig()):
        self.config = config

    def collate(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """Collate a list of feature dicts into a batch."""
        if not features:
            return {}

        # Determine keys and max lengths
        keys = set()
        for f in features:
            keys.update(f.keys())

        batch = {}
        for key in keys:
            values = [f.get(key) for f in features if key in f]
            if not values:
                continue

            if isinstance(values[0], (list, torch.Tensor)):
                batch[key] = self._pad_sequences(values, key)
            elif isinstance(values[0], (int, float)):
                batch[key] = torch.tensor(values)
            elif isinstance(values[0], str):
                batch[key] = values  # Keep as list

        # Create attention mask if input_ids present
        if "input_ids" in batch and "attention_mask" not in batch:
            batch["attention_mask"] = (batch["input_ids"] != self.config.pad_token_id).long()

        return batch

    def _pad_sequences(self, sequences: List, key: str) -> torch.Tensor:
        """Pad variable-length sequences to uniform length."""
        # Convert to tensors if needed
        tensors = []
        for seq in sequences:
            if isinstance(seq, list):
                tensors.append(torch.tensor(seq))
            elif isinstance(seq, torch.Tensor):
                tensors.append(seq)
            else:
                continue

        if not tensors:
            return torch.tensor([])

        # Determine target length
        lengths = [t.shape[0] for t in tensors]
        max_len = max(lengths)

        if self.config.max_length:
            max_len = min(max_len, self.config.max_length)

        # Round up to multiple
        if self.config.pad_to_multiple_of > 1:
            max_len = math.ceil(max_len / self.config.pad_to_multiple_of) * self.config.pad_to_multiple_of

        # Determine pad value
        pad_value = self.config.pad_token_id
        if "label" in key:
            pad_value = self.config.label_pad_id

        # Pad
        padded = []
        for t in tensors:
            if t.shape[0] > max_len:
                t = t[:max_len]
            if t.shape[0] < max_len:
                padding = torch.full((max_len - t.shape[0],) + t.shape[1:],
                                     pad_value, dtype=t.dtype)
                t = torch.cat([t, padding])
            padded.append(t)

        return torch.stack(padded)

    def collate_with_mlm(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """Collate with Masked Language Modeling."""
        batch = self.collate(features)

        if "input_ids" not in batch:
            return batch

        input_ids = batch["input_ids"].clone()
        labels = input_ids.clone()

        # Create random mask
        probability_matrix = torch.full(input_ids.shape, self.config.mlm_probability)

        # Don't mask padding or special tokens
        padding_mask = input_ids == self.config.pad_token_id
        probability_matrix.masked_fill_(padding_mask, 0.0)

        masked_indices = torch.bernoulli(probability_matrix).bool()
        labels[~masked_indices] = self.config.label_pad_id

        # 80% replace with [MASK]
        indices_replaced = torch.bernoulli(
            torch.full(input_ids.shape, 0.8)
        ).bool() & masked_indices
        input_ids[indices_replaced] = self.config.mask_token_id

        # 10% replace with random token
        indices_random = torch.bernoulli(
            torch.full(input_ids.shape, 0.5)
        ).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(
            5, 30000, input_ids.shape, dtype=input_ids.dtype
        )
        input_ids[indices_random] = random_words[indices_random]

        # 10% keep original

        batch["input_ids"] = input_ids
        batch["labels"] = labels
        return batch


class SequenceBucketer:
    """Group sequences by length for efficient batching."""

    def __init__(self, bucket_boundaries: List[int] = None,
                 num_buckets: int = 8, max_length: int = 2048):
        if bucket_boundaries:
            self.boundaries = sorted(bucket_boundaries)
        else:
            step = max_length // num_buckets
            self.boundaries = [step * (i + 1) for i in range(num_buckets)]

    def assign_bucket(self, length: int) -> int:
        for i, boundary in enumerate(self.boundaries):
            if length <= boundary:
                return i
        return len(self.boundaries)

    def bucket_batch(self, features: List[Dict[str, Any]],
                     batch_size: int,
                     length_key: str = "input_ids") -> List[List[Dict[str, Any]]]:
        """Sort features into length-bucketed batches."""
        # Assign buckets
        buckets: Dict[int, List] = {}
        for f in features:
            length = len(f.get(length_key, []))
            bucket_id = self.assign_bucket(length)
            if bucket_id not in buckets:
                buckets[bucket_id] = []
            buckets[bucket_id].append(f)

        # Create batches from each bucket
        batches = []
        for bucket_id in sorted(buckets.keys()):
            bucket = buckets[bucket_id]
            random.shuffle(bucket)
            for i in range(0, len(bucket), batch_size):
                batches.append(bucket[i:i + batch_size])

        random.shuffle(batches)
        return batches


class MultiModalCollator:
    """Collator for multi-modal inputs (text + audio + vision)."""

    def __init__(self, text_config: CollatorConfig = CollatorConfig(),
                 audio_max_frames: int = 1024,
                 image_size: Tuple[int, int] = (224, 224)):
        self.text_collator = OmniDataCollator(text_config)
        self.audio_max_frames = audio_max_frames
        self.image_size = image_size

    def collate(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        """Collate multi-modal features into a single batch."""
        batch = {}

        # Text features
        text_features = [
            {k: v for k, v in f.items() if k.startswith("text_")}
            for f in features
        ]
        if any(text_features):
            text_batch = self.text_collator.collate(text_features)
            batch.update(text_batch)

        # Audio features
        audio_data = [f.get("audio_features") for f in features
                      if "audio_features" in f]
        if audio_data:
            batch["audio_features"] = self._pad_audio(audio_data)
            batch["audio_mask"] = self._create_audio_mask(audio_data)

        # Vision features
        image_data = [f.get("pixel_values") for f in features
                      if "pixel_values" in f]
        if image_data:
            batch["pixel_values"] = torch.stack([
                self._resize_image(img) for img in image_data
            ])

        # Modality indicators
        batch["modality_mask"] = torch.tensor([
            [int("text_input_ids" in f),
             int("audio_features" in f),
             int("pixel_values" in f)]
            for f in features
        ], dtype=torch.long)

        return batch

    def _pad_audio(self, audio_list: List) -> torch.Tensor:
        tensors = [torch.tensor(a) if not isinstance(a, torch.Tensor) else a
                   for a in audio_list]
        max_frames = min(max(t.shape[0] for t in tensors), self.audio_max_frames)
        n_mels = tensors[0].shape[1] if tensors[0].dim() > 1 else 1

        padded = []
        for t in tensors:
            if t.shape[0] > max_frames:
                t = t[:max_frames]
            elif t.shape[0] < max_frames:
                pad_size = max_frames - t.shape[0]
                if t.dim() > 1:
                    padding = torch.zeros(pad_size, t.shape[1])
                else:
                    padding = torch.zeros(pad_size)
                t = torch.cat([t, padding])
            padded.append(t)

        return torch.stack(padded)

    def _create_audio_mask(self, audio_list: List) -> torch.Tensor:
        lengths = [len(a) if isinstance(a, list) else a.shape[0]
                   for a in audio_list]
        max_len = min(max(lengths), self.audio_max_frames)
        return torch.tensor([[1] * min(l, max_len) + [0] * (max_len - min(l, max_len))
                             for l in lengths])

    def _resize_image(self, img: torch.Tensor) -> torch.Tensor:
        if not isinstance(img, torch.Tensor):
            img = torch.tensor(img)
        # Simple bilinear resize
        if img.dim() == 3:
            img = img.unsqueeze(0)
        if img.shape[-2:] != self.image_size:
            img = torch.nn.functional.interpolate(
                img.float(), size=self.image_size, mode="bilinear",
                align_corners=False
            )
        return img.squeeze(0)
