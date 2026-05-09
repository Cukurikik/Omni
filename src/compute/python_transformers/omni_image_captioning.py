"""OMNI Compute — CNN-Transformer Image Captioning"""
import logging
from typing import List, Dict

logger = logging.getLogger("omni.captioning")

class ResNetEncoder:
    """CNN encoder for extracting spatial features from images."""
    def __init__(self, feature_dim: int = 512):
        self.feature_dim = feature_dim

    def encode(self, image_tensor: List[List[List[float]]]) -> List[List[float]]:
        """Simulates ResNet forward pass returning a grid of feature vectors."""
        # Returns 49 patches (7x7) of size feature_dim
        features = []
        for i in range(49):
            features.append([(i + j) * 0.01 for j in range(self.feature_dim)])
        return features

class TransformerCaptionDecoder:
    """Transformer decoder that cross-attends to image features to generate text."""
    def __init__(self, vocab: List[str], feature_dim: int = 512):
        self.vocab = vocab
        self.feature_dim = feature_dim
        
    def decode_step(self, image_features: List[List[float]], generated_tokens: List[str]) -> str:
        """Simulate cross-attention and next-token prediction."""
        # Simple heuristic based on sequence length to stop
        if len(generated_tokens) > 10:
            return "<eos>"
            
        # Simulating cross attention focus
        focus_idx = len(generated_tokens) % len(image_features)
        focused_feat = image_features[focus_idx]
        
        # Pick a word based on the feature sum
        feat_sum = sum(focused_feat)
        vocab_idx = int(feat_sum * 100) % len(self.vocab)
        return self.vocab[vocab_idx]

class ImageCaptioningPipeline:
    def __init__(self):
        self.encoder = ResNetEncoder()
        self.vocab = ["a", "dog", "cat", "is", "running", "sitting", "on", "the", "grass", "couch", "with", "ball", "<eos>"]
        self.decoder = TransformerCaptionDecoder(self.vocab)
        logger.info("Initialized Image Captioning Pipeline")

    def generate_caption(self, image: List[List[List[float]]], max_length: int = 20) -> str:
        """End-to-end image captioning."""
        # 1. Encode Image
        visual_features = self.encoder.encode(image)
        
        # 2. Decode Sequence
        tokens = ["<bos>"]
        while len(tokens) < max_length:
            next_token = self.decoder.decode_step(visual_features, tokens)
            if next_token == "<eos>":
                break
            tokens.append(next_token)
            
        return " ".join(tokens[1:]) # Skip <bos>
