"""OMNI Compute — Early Convolution Table Structure Recognizer"""
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger("omni.tsr")

class ConvStem:
    """Early convolutions for visual feature extraction prior to Transformer."""
    def __init__(self, in_channels: int = 3, out_channels: int = 64):
        self.in_channels = in_channels
        self.out_channels = out_channels
        
    def extract(self, image: List[List[List[float]]]) -> List[List[float]]:
        """Simulates Conv2D -> BatchNorm -> ReLU -> MaxPool"""
        features = []
        # Downsample and extract visual features
        for y in range(0, len(image), 4):
            row_feat = []
            for x in range(0, len(image[0]), 4):
                val = sum(image[y][x]) / max(self.in_channels, 1)
                row_feat.append(max(0.0, val)) # ReLU
            features.append(row_feat)
        return features

class TSRTransformer:
    """Table Structure Recognition Transformer with Convolutional Stem."""
    def __init__(self):
        self.stem = ConvStem()
        logger.info("Initialized TSR-ConvStem Transformer")

    def _decoder_step(self, encoder_memory: List[List[float]], prev_token: str) -> Tuple[str, List[float]]:
        """Simulate single decoder step returning tag and bounding box."""
        if prev_token == "<s>":
            return "<thead>", [0.0, 0.0, 1.0, 0.1]
        elif prev_token == "<thead>":
            return "<tr>", [0.0, 0.0, 1.0, 0.1]
        elif prev_token == "<tr>":
            return "<td>", [0.0, 0.0, 0.5, 0.1]
        elif prev_token == "<td>":
            return "</td>", [0.0, 0.0, 0.5, 0.1]
        elif prev_token == "</td>":
            return "</tr>", [0.0, 0.0, 1.0, 0.1]
        else:
            return "</s>", [0.0, 0.0, 0.0, 0.0]

    def recognize(self, image_tensor: List[List[List[float]]]) -> Dict[str, Any]:
        """
        Takes an image tensor of a document and returns the HTML structure
        and bounding boxes of the table cells.
        """
        # 1. Early Convolutions (ConvStem)
        visual_features = self.stem.extract(image_tensor)
        
        # 2. Flatten for Transformer Encoder
        flat_features = []
        for row in visual_features:
            flat_features.extend(row)
            
        # 3. Autoregressive Decoding
        html_tokens = []
        bboxes = []
        
        curr_token = "<s>"
        max_steps = 100
        step = 0
        
        while curr_token != "</s>" and step < max_steps:
            next_token, bbox = self._decoder_step(flat_features, curr_token)
            html_tokens.append(next_token)
            if next_token in ["<td>", "<th>"]:
                bboxes.append({"token": next_token, "box": bbox})
            curr_token = next_token
            step += 1
            
        return {
            "html": "".join(html_tokens),
            "cells": bboxes,
            "feature_map_size": len(flat_features)
        }
