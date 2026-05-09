"""
omni_stale_loader.py — STALE Dataloader
Inspired by: STALE (Zero-Shot Temporal Action Detection)
Layer: Compute / AI

Dataloader for processing unconstrained video streams into temporal segments
and extracting CLIP/ViT visual features alongside text prompt representations.
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import List, Dict, Tuple
import os

class OmniActionDetectionDataset(Dataset):
    """
    Dataset loader for extracting segment-level visual features from videos
    and aligning them with zero-shot text action prompts.
    """

    def __init__(self, feature_dir: str, annotation_file: str, num_segments: int = 100):
        super().__init__()
        self.feature_dir = feature_dir
        self.num_segments = num_segments
        
        # Load mock annotations (e.g., {"video_1": [{"label": "running", "start": 10.5, "end": 15.0}]})
        self.annotations = self._load_annotations(annotation_file)
        self.video_ids = list(self.annotations.keys())
        
    def _load_annotations(self, path: str) -> Dict[str, List[Dict]]:
        # In production, parses THUMOS14 or ActivityNet JSON format
        return {
            "vid_001": [{"label": "jump", "start": 2.0, "end": 4.5}],
            "vid_002": [{"label": "swim", "start": 0.0, "end": 10.0}]
        }

    def _load_features(self, video_id: str) -> torch.Tensor:
        """
        Loads pre-extracted frame features (e.g., from CLIP/I3D).
        Pads or interpolates temporal features to exactly `num_segments`.
        """
        feat_path = os.path.join(self.feature_dir, f"{video_id}.npy")
        if os.path.exists(feat_path):
            feats = np.load(feat_path)
        else:
            # Mocking features: shape (T, D) -> e.g., (120, 512)
            feats = np.random.randn(120, 512).astype(np.float32)
            
        feats_tensor = torch.from_numpy(feats)
        
        # Interpolate temporally to fixed segments
        feats_tensor = feats_tensor.unsqueeze(0).permute(0, 2, 1) # (1, D, T)
        feats_tensor = torch.nn.functional.interpolate(feats_tensor, size=self.num_segments, mode='linear', align_corners=False)
        feats_tensor = feats_tensor.squeeze(0).permute(1, 0) # (num_segments, D)
        
        return feats_tensor

    def __len__(self) -> int:
        return len(self.video_ids)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        vid_id = self.video_ids[idx]
        visual_features = self._load_features(vid_id)
        
        # Binary target matrix (num_segments, num_classes)
        # Mock class "0" is jump, "1" is swim, etc.
        targets = torch.zeros(self.num_segments, 10, dtype=torch.float32)
        
        return {
            "video_id": vid_id,
            "features": visual_features,
            "targets": targets
        }

def get_stale_dataloader(feature_dir: str, batch_size: int = 16) -> DataLoader:
    dataset = OmniActionDetectionDataset(feature_dir, "annotations.json")
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)
