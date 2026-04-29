"""
OMNI MMF (Multimodal Framework) Engine
========================================
Production-grade multimodal AI research engine inspired by facebookresearch/mmf.
Implements modular components for vision-language tasks: VQA, image captioning,
visual reasoning, and multimodal fusion.

Extracted Patterns:
  - Registry pattern for dynamic model/dataset/loss/metric registration
  - Modular Encoder architecture (ImageEncoder, TextEncoder)
  - Multimodal fusion strategies (concatenation, element-wise, bilinear, attention)
  - Task-specific heads (VQA classification, caption generation)
  - SampleList / Sample abstraction for batch data
  - Config-driven architecture composition
  - Metric computation (VQA accuracy, BLEU, CIDEr approximations)
  - Preprocessing pipelines for text tokenization and image normalization

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from enum import Enum
from collections import OrderedDict

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class MMFError(Exception):
    """Base error for MMF engine."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. REGISTRY PATTERN
# ---------------------------------------------------------------------------

class Registry:
    """
    Central registry for models, datasets, losses, metrics, processors.

    Implements the facebookresearch/mmf Registry pattern that allows
    dynamic registration and lookup of any component by name.
    """

    def __init__(self):
        """Initialize Registry."""
        self._registries: Dict[str, Dict[str, Any]] = {
            "model": {},
            "dataset": {},
            "loss": {},
            "metric": {},
            "processor": {},
            "fusion": {},
            "encoder": {},
            "task": {},
        }

    def register(self, category: str, name: str, obj: Any) -> Result:
        """Register an object under a category."""
        if category not in self._registries:
            return Err(f"Unknown registry category: {category}")
        self._registries[category][name] = obj
        return Ok(name)

    def get(self, category: str, name: str) -> Result:
        """Look up a registered object."""
        if category not in self._registries:
            return Err(f"Unknown registry category: {category}")
        if name not in self._registries[category]:
            return Err(f"'{name}' not found in '{category}' registry")
        return Ok(self._registries[category][name])

    def list_registered(self, category: str) -> List[str]:
        """List all names in a category."""
        return list(self._registries.get(category, {}).keys())

    def categories(self) -> List[str]:
        """List all registry categories."""
        return list(self._registries.keys())


# ---------------------------------------------------------------------------
# 3. SAMPLE & SAMPLELIST (Data Abstraction)
# ---------------------------------------------------------------------------

@dataclass
class Sample:
    """
    Single data sample for multimodal tasks.

    Holds fields analogous to MMF's Sample:
    image features, text tokens, targets, metadata.
    """
    id: str = ""
    image_features: Optional[np.ndarray] = None       # (regions, feat_dim)
    text_tokens: Optional[np.ndarray] = None           # (seq_len,) int
    text_embeddings: Optional[np.ndarray] = None       # (seq_len, emb_dim)
    targets: Optional[np.ndarray] = None               # task-specific
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_image(self) -> bool:
        """Check if image condition holds."""
        return self.image_features is not None

    def has_text(self) -> bool:
        """Check if text condition holds."""
        return self.text_tokens is not None or self.text_embeddings is not None


class SampleList:
    """
    Batch of Samples with collation support.

    Mimics MMF's SampleList for batched multimodal data.
    """

    def __init__(self, samples: List[Sample]):
        """Initialize SampleList."""
        self.samples = samples

    @property
    def batch_size(self) -> int:
        """Execute batch size operation for SampleList."""
        return len(self.samples)

    def get_image_features(self) -> Optional[np.ndarray]:
        """Stack image features across batch."""
        feats = [s.image_features for s in self.samples if s.image_features is not None]
        if not feats:
            return None
        return np.stack(feats)

    def get_text_tokens(self) -> Optional[np.ndarray]:
        """Stack text tokens across batch."""
        tokens = [s.text_tokens for s in self.samples if s.text_tokens is not None]
        if not tokens:
            return None
        max_len = max(t.shape[0] for t in tokens)
        padded = np.zeros((len(tokens), max_len), dtype=np.int64)
        for i, t in enumerate(tokens):
            padded[i, :t.shape[0]] = t
        return padded

    def get_targets(self) -> Optional[np.ndarray]:
        """Stack targets across batch."""
        targets = [s.targets for s in self.samples if s.targets is not None]
        if not targets:
            return None
        return np.stack(targets)


# ---------------------------------------------------------------------------
# 4. HELPERS
# ---------------------------------------------------------------------------

def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax."""
    e = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e / (np.sum(e, axis=axis, keepdims=True) + 1e-10)


def layer_norm(x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Layer normalization."""
    mean = np.mean(x, axis=-1, keepdims=True)
    var = np.var(x, axis=-1, keepdims=True)
    return (x - mean) / np.sqrt(var + eps)


def gelu(x: np.ndarray) -> np.ndarray:
    """Gaussian Error Linear Unit activation."""
    return 0.5 * x * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x ** 3)))


def cross_entropy(logits: np.ndarray, targets: np.ndarray) -> float:
    """Cross-entropy loss. targets: (batch,) integers."""
    probs = softmax(logits, axis=-1)
    b = logits.shape[0]
    loss = 0.0
    for i in range(b):
        t = int(np.clip(targets[i], 0, logits.shape[1] - 1))
        loss -= np.log(probs[i, t] + 1e-10)
    return float(loss / max(b, 1))


def binary_cross_entropy(logits: np.ndarray, targets: np.ndarray) -> float:
    """Binary cross-entropy for multi-label / VQA soft targets."""
    sigmoid = 1.0 / (1.0 + np.exp(-np.clip(logits, -20, 20)))
    loss = -(targets * np.log(sigmoid + 1e-10) + (1 - targets) * np.log(1 - sigmoid + 1e-10))
    return float(np.mean(loss))


# ---------------------------------------------------------------------------
# 5. ENCODERS
# ---------------------------------------------------------------------------

class ImageEncoder:
    """
    Image feature encoder.

    Projects raw or pre-extracted image features to a common
    embedding dimension. Supports linear or two-layer projection.
    """

    def __init__(self, input_dim: int = 2048, output_dim: int = 512,
                 use_layer_norm: bool = True):
        """Initialize ImageEncoder."""
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.use_layer_norm = use_layer_norm

        scale = 1.0 / math.sqrt(input_dim)
        self.W1 = np.random.randn(input_dim, output_dim).astype(np.float32) * scale
        self.b1 = np.zeros(output_dim, dtype=np.float32)

    def encode(self, features: np.ndarray) -> np.ndarray:
        """
        Encode image features.

        Args:
            features: (..., input_dim)

        Returns:
            encoded: (..., output_dim)
        """
        out = features @ self.W1 + self.b1
        out = gelu(out)
        if self.use_layer_norm:
            out = layer_norm(out)
        return out


class TextEncoder:
    """
    Text token encoder with positional embeddings.

    Embeds tokens and adds sinusoidal positional encodings.
    """

    def __init__(self, vocab_size: int = 30000, embed_dim: int = 512,
                 max_seq_len: int = 128):
        """Initialize TextEncoder."""
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len

        self.token_emb = np.random.randn(vocab_size, embed_dim).astype(np.float32) * 0.02
        self.pos_enc = self._sinusoidal_pos(max_seq_len, embed_dim)

    def _sinusoidal_pos(self, max_len: int, dim: int) -> np.ndarray:
        """Sinusoidal positional encoding (as in Vaswani et al.)."""
        pe = np.zeros((max_len, dim), dtype=np.float32)
        positions = np.arange(max_len, dtype=np.float32)[:, None]
        div_term = np.exp(np.arange(0, dim, 2, dtype=np.float32) * -(math.log(10000.0) / dim))
        pe[:, 0::2] = np.sin(positions * div_term)
        pe[:, 1::2] = np.cos(positions * div_term)
        return pe

    def encode(self, tokens: np.ndarray) -> np.ndarray:
        """
        Encode text tokens.

        Args:
            tokens: (batch, seq_len) int

        Returns:
            embeddings: (batch, seq_len, embed_dim)
        """
        tokens_clipped = np.clip(tokens, 0, self.vocab_size - 1)
        emb = self.token_emb[tokens_clipped]
        seq_len = tokens_clipped.shape[1]
        emb = emb + self.pos_enc[:seq_len]
        return layer_norm(emb)


# ---------------------------------------------------------------------------
# 6. MULTIMODAL FUSION STRATEGIES
# ---------------------------------------------------------------------------

class FusionType(Enum):
    """Type enumeration for FusionType."""
    CONCAT = "concat"
    ELEMENT_WISE = "element_wise"
    BILINEAR = "bilinear"
    ATTENTION = "attention"


class ConcatFusion:
    """Concatenation-based multimodal fusion."""

    def fuse(self, image_feat: np.ndarray, text_feat: np.ndarray) -> np.ndarray:
        """
        Concatenate image and text features.

        Args:
            image_feat: (batch, img_dim)
            text_feat:  (batch, txt_dim)

        Returns:
            fused: (batch, img_dim + txt_dim)
        """
        return np.concatenate([image_feat, text_feat], axis=-1)


class ElementWiseFusion:
    """Element-wise product/sum fusion."""

    def __init__(self, dim: int = 512, operation: str = "mul"):
        """Initialize ElementWiseFusion."""
        self.operation = operation
        scale = 1.0 / math.sqrt(dim)
        self.W_img = np.random.randn(dim, dim).astype(np.float32) * scale
        self.W_txt = np.random.randn(dim, dim).astype(np.float32) * scale

    def fuse(self, image_feat: np.ndarray, text_feat: np.ndarray) -> np.ndarray:
        """Element-wise fusion after projection."""
        img_proj = image_feat @ self.W_img
        txt_proj = text_feat @ self.W_txt
        if self.operation == "mul":
            return img_proj * txt_proj
        return img_proj + txt_proj


class BilinearFusion:
    """
    Bilinear pooling fusion.

    Computes z = x^T W y for each sample, approximated
    via low-rank factorization.
    """

    def __init__(self, img_dim: int = 512, txt_dim: int = 512,
                 output_dim: int = 512, rank: int = 64):
        """Initialize BilinearFusion."""
        self.rank = rank
        scale = 1.0 / math.sqrt(rank)
        self.P = np.random.randn(img_dim, rank).astype(np.float32) * scale
        self.Q = np.random.randn(txt_dim, rank).astype(np.float32) * scale
        self.W_out = np.random.randn(rank, output_dim).astype(np.float32) * scale

    def fuse(self, image_feat: np.ndarray, text_feat: np.ndarray) -> np.ndarray:
        """Low-rank bilinear fusion."""
        img_proj = image_feat @ self.P  # (B, rank)
        txt_proj = text_feat @ self.Q   # (B, rank)
        interaction = img_proj * txt_proj
        return np.tanh(interaction @ self.W_out)


class AttentionFusion:
    """
    Cross-attention fusion.

    Text attends to image regions (or vice versa) for
    fine-grained multimodal alignment.
    """

    def __init__(self, dim: int = 512, n_heads: int = 8):
        """Initialize AttentionFusion."""
        self.dim = dim
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        scale = 1.0 / math.sqrt(self.head_dim)
        self.W_q = np.random.randn(dim, dim).astype(np.float32) * scale
        self.W_k = np.random.randn(dim, dim).astype(np.float32) * scale
        self.W_v = np.random.randn(dim, dim).astype(np.float32) * scale
        self.W_o = np.random.randn(dim, dim).astype(np.float32) * scale

    def fuse(self, query: np.ndarray, context: np.ndarray) -> np.ndarray:
        """
        Cross-attention fusion.

        Args:
            query:   (batch, q_len, dim) — text embeddings
            context: (batch, c_len, dim) — image region features

        Returns:
            attended: (batch, q_len, dim)
        """
        b, q_len, d = query.shape
        _, c_len, _ = context.shape

        Q = (query @ self.W_q).reshape(b, q_len, self.n_heads, self.head_dim).transpose(0, 2, 1, 3)
        K = (context @ self.W_k).reshape(b, c_len, self.n_heads, self.head_dim).transpose(0, 2, 1, 3)
        V = (context @ self.W_v).reshape(b, c_len, self.n_heads, self.head_dim).transpose(0, 2, 1, 3)

        scores = Q @ K.transpose(0, 1, 3, 2) / math.sqrt(self.head_dim)
        attn = softmax(scores, axis=-1)
        out = attn @ V  # (B, H, q_len, head_dim)
        out = out.transpose(0, 2, 1, 3).reshape(b, q_len, d)
        return out @ self.W_o


# ---------------------------------------------------------------------------
# 7. TASK HEADS
# ---------------------------------------------------------------------------

class VQAHead:
    """
    VQA classification head.

    Projects fused multimodal features to answer vocabulary.
    """

    def __init__(self, input_dim: int = 512, num_answers: int = 3129):
        """Initialize VQAHead."""
        self.num_answers = num_answers
        scale = 1.0 / math.sqrt(input_dim)
        self.W1 = np.random.randn(input_dim, input_dim).astype(np.float32) * scale
        self.b1 = np.zeros(input_dim, dtype=np.float32)
        self.W2 = np.random.randn(input_dim, num_answers).astype(np.float32) * scale
        self.b2 = np.zeros(num_answers, dtype=np.float32)

    def forward(self, features: np.ndarray) -> np.ndarray:
        """
        Predict answer logits.

        Args:
            features: (batch, input_dim)

        Returns:
            logits: (batch, num_answers)
        """
        h = gelu(features @ self.W1 + self.b1)
        h = layer_norm(h)
        return h @ self.W2 + self.b2


class CaptionHead:
    """
    Caption generation head.

    Autoregressive generation of caption tokens given
    image features.
    """

    def __init__(self, dim: int = 512, vocab_size: int = 10000,
                 max_caption_len: int = 32):
        """Initialize CaptionHead."""
        self.dim = dim
        self.vocab_size = vocab_size
        self.max_caption_len = max_caption_len

        scale = 1.0 / math.sqrt(dim)
        self.W_proj = np.random.randn(dim, vocab_size).astype(np.float32) * scale

    def forward(self, features: np.ndarray) -> np.ndarray:
        """
        Project features to caption vocabulary logits.

        Args:
            features: (batch, dim)

        Returns:
            logits: (batch, vocab_size)
        """
        return features @ self.W_proj

    def generate(self, features: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        """
        Generate caption token sequence.

        Args:
            features: (batch, dim)

        Returns:
            tokens: (batch, max_caption_len)
        """
        b = features.shape[0]
        tokens = np.zeros((b, self.max_caption_len), dtype=np.int64)

        current = features
        for t in range(self.max_caption_len):
            logits = self.forward(current) / max(temperature, 1e-8)
            probs = softmax(logits, axis=-1)
            # Sample from distribution
            for bi in range(b):
                tokens[bi, t] = np.self.vocab_size, p=probs[bi][int(hashlib.sha256(b"det").hexdigest()[:8], 16) % max(1, len(self.vocab_size, p=probs[bi]))]
            # Simple update: mix features with token embedding
            token_emb = np.random.randn(b, self.dim).astype(np.float32) * 0.01
            current = 0.8 * current + 0.2 * token_emb

        return tokens


# ---------------------------------------------------------------------------
# 8. METRICS
# ---------------------------------------------------------------------------

def vqa_accuracy(predictions: np.ndarray, targets: np.ndarray) -> float:
    """
    VQA accuracy with soft scoring.

    For VQA 2.0: min(#humans_who_said_that / 3, 1)
    Here simplified to argmax match.

    Args:
        predictions: (batch, num_answers) logits
        targets: (batch, num_answers) soft target or (batch,) hard targets

    Returns:
        accuracy: float [0, 1]
    """
    pred_answers = np.argmax(predictions, axis=-1)
    if targets.ndim == 1:
        return float(np.mean(pred_answers == targets))
    # Soft targets
    target_answers = np.argmax(targets, axis=-1)
    return float(np.mean(pred_answers == target_answers))


def bleu_score(reference_tokens: np.ndarray, hypothesis_tokens: np.ndarray,
               max_n: int = 4) -> float:
    """
    Simplified BLEU score computation.

    Computes n-gram precision for n=1..max_n with brevity penalty.
    """
    ref = reference_tokens.flatten().tolist()
    hyp = hypothesis_tokens.flatten().tolist()

    if len(hyp) == 0:
        return 0.0

    # Brevity penalty
    bp = min(1.0, math.exp(1.0 - len(ref) / max(len(hyp), 1)))

    precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams: Dict[Tuple, int] = {}
        for i in range(len(ref) - n + 1):
            ng = tuple(ref[i:i+n])
            ref_ngrams[ng] = ref_ngrams.get(ng, 0) + 1

        matches = 0
        total = 0
        hyp_ngrams: Dict[Tuple, int] = {}
        for i in range(len(hyp) - n + 1):
            ng = tuple(hyp[i:i+n])
            hyp_ngrams[ng] = hyp_ngrams.get(ng, 0) + 1

        for ng, count in hyp_ngrams.items():
            matches += min(count, ref_ngrams.get(ng, 0))
            total += count

        precision = matches / max(total, 1)
        precisions.append(max(precision, 1e-10))

    log_avg = sum(math.log(p) for p in precisions) / max_n
    return bp * math.exp(log_avg)


def cider_score_approx(reference_tokens: np.ndarray,
                       hypothesis_tokens: np.ndarray) -> float:
    """
    Approximate CIDEr score using TF-IDF weighted n-gram similarity.

    This is a simplified version focused on capturing the CIDEr approach.
    """
    ref = reference_tokens.flatten().tolist()
    hyp = hypothesis_tokens.flatten().tolist()

    if len(hyp) == 0 or len(ref) == 0:
        return 0.0

    # Compute 4-gram TF vectors
    def get_tf(tokens: list, n: int = 4) -> Dict[Tuple, float]:
        ngrams: Dict[Tuple, float] = {}
        total = max(len(tokens) - n + 1, 1)
        for i in range(len(tokens) - n + 1):
            ng = tuple(tokens[i:i+n])
            ngrams[ng] = ngrams.get(ng, 0) + 1.0
        for ng in ngrams:
            ngrams[ng] /= total
        return ngrams

    ref_tf = get_tf(ref)
    hyp_tf = get_tf(hyp)

    # Cosine similarity between TF vectors
    all_ngrams = set(ref_tf.keys()) | set(hyp_tf.keys())
    if not all_ngrams:
        return 0.0

    dot = sum(ref_tf.get(ng, 0) * hyp_tf.get(ng, 0) for ng in all_ngrams)
    norm_ref = math.sqrt(sum(v**2 for v in ref_tf.values()) + 1e-10)
    norm_hyp = math.sqrt(sum(v**2 for v in hyp_tf.values()) + 1e-10)

    return 10.0 * dot / (norm_ref * norm_hyp)  # CIDEr scale factor


# ---------------------------------------------------------------------------
# 9. PREPROCESSORS
# ---------------------------------------------------------------------------

class TextTokenizer:
    """
    Simple whitespace + character-level tokenizer.

    Production systems would use BPE or SentencePiece.
    """

    def __init__(self, vocab_size: int = 30000, max_seq_len: int = 128):
        """Initialize TextTokenizer."""
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self._pad_id = 0
        self._unk_id = 1
        self._bos_id = 2
        self._eos_id = 3

    def tokenize(self, text: str) -> np.ndarray:
        """Tokenize text to integer tokens."""
        tokens = [self._bos_id]
        for ch in text.lower():
            code = ord(ch) % (self.vocab_size - 4) + 4
            tokens.append(code)
        tokens.append(self._eos_id)

        # Pad or truncate
        if len(tokens) >= self.max_seq_len:
            tokens = tokens[:self.max_seq_len]
        else:
            tokens.extend([self._pad_id] * (self.max_seq_len - len(tokens)))

        return np.array(tokens, dtype=np.int64)


class ImagePreprocessor:
    """
    Image preprocessing pipeline.

    Normalizes images to ImageNet statistics and extracts
    pseudo-features for multimodal fusion.
    """

    def __init__(self, feature_dim: int = 2048, num_regions: int = 36):
        """Initialize ImagePreprocessor."""
        self.feature_dim = feature_dim
        self.num_regions = num_regions
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize image with ImageNet stats. Input (H, W, 3) or (B, H, W, 3)."""
        img = image.astype(np.float32) / 255.0
        return (img - self.mean) / (self.std + 1e-8)

    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """
        Extract pseudo-region features from normalized image.

        In production, this would be a Faster-RCNN backbone.

        Args:
            image: (H, W, 3)

        Returns:
            features: (num_regions, feature_dim)
        """
        h, w = image.shape[:2]
        grid_h = int(math.sqrt(self.num_regions))
        grid_w = self.num_regions // grid_h

        patch_h = h // grid_h
        patch_w = w // grid_w
        features = np.zeros((grid_h * grid_w, self.feature_dim), dtype=np.float32)

        for i in range(grid_h):
            for j in range(grid_w):
                patch = image[i*patch_h:(i+1)*patch_h, j*patch_w:(j+1)*patch_w]
                # Compute statistical features from patch
                flat = patch.flatten().astype(np.float32)
                # Project to feature_dim via hash-like projection
                idx = i * grid_w + j
                np.random.seed(idx)
                proj = np.random.randn(flat.shape[0], self.feature_dim).astype(np.float32) * 0.001
                features[idx] = flat @ proj[:flat.shape[0]]

        return features


# ---------------------------------------------------------------------------
# 10. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniMMFEngine:
    """
    Production-grade Multimodal Framework engine for OMNI.

    Provides:
      - Registry: dynamic component registration
      - Encoders: ImageEncoder, TextEncoder with sinusoidal position
      - Fusion: Concat, Element-wise, Bilinear, Cross-Attention
      - Task heads: VQA classification, Caption generation
      - Metrics: VQA accuracy, BLEU, CIDEr approximation
      - Preprocessing: tokenizer, image normalizer
      - Full VQA and captioning pipelines
    """

    VERSION = "1.0.0"
    ENGINE_ID = "omni-mmf"

    def __init__(
        self,
        img_feat_dim: int = 2048,
        embed_dim: int = 512,
        vocab_size: int = 30000,
        num_answers: int = 3129,
        max_seq_len: int = 128,
        num_regions: int = 36,
        fusion_type: str = "concat",
    ):
        """Initialize OmniMMFEngine."""
        self.embed_dim = embed_dim
        self.vocab_size = vocab_size
        self.num_answers = num_answers

        # Registry
        self.registry = Registry()

        # Encoders
        self.image_encoder = ImageEncoder(img_feat_dim, embed_dim)
        self.text_encoder = TextEncoder(vocab_size, embed_dim, max_seq_len)

        # Fusion
        self.fusion_type = FusionType(fusion_type)
        if self.fusion_type == FusionType.CONCAT:
            self.fusion = ConcatFusion()
            vqa_input_dim = embed_dim * 2
        elif self.fusion_type == FusionType.ELEMENT_WISE:
            self.fusion = ElementWiseFusion(embed_dim)
            vqa_input_dim = embed_dim
        elif self.fusion_type == FusionType.BILINEAR:
            self.fusion = BilinearFusion(embed_dim, embed_dim, embed_dim)
            vqa_input_dim = embed_dim
        else:
            self.fusion = AttentionFusion(embed_dim)
            vqa_input_dim = embed_dim

        # Task heads
        self.vqa_head = VQAHead(vqa_input_dim, num_answers)
        self.caption_head = CaptionHead(embed_dim, vocab_size)

        # Preprocessors
        self.tokenizer = TextTokenizer(vocab_size, max_seq_len)
        self.image_preprocessor = ImagePreprocessor(img_feat_dim, num_regions)

        # Register default components
        self._register_defaults()

    def _register_defaults(self):
        """Register built-in components."""
        self.registry.register("encoder", "image", self.image_encoder)
        self.registry.register("encoder", "text", self.text_encoder)
        self.registry.register("fusion", "concat", ConcatFusion)
        self.registry.register("fusion", "element_wise", ElementWiseFusion)
        self.registry.register("fusion", "bilinear", BilinearFusion)
        self.registry.register("fusion", "attention", AttentionFusion)
        self.registry.register("metric", "vqa_accuracy", vqa_accuracy)
        self.registry.register("metric", "bleu", bleu_score)
        self.registry.register("metric", "cider", cider_score_approx)

    # --- Sample creation ---

    def create_sample(self, image: Optional[np.ndarray] = None,
                      text: Optional[str] = None,
                      targets: Optional[np.ndarray] = None,
                      sample_id: str = "") -> Sample:
        """Create a multimodal Sample."""
        img_feat = None
        txt_tok = None

        if image is not None:
            normalized = self.image_preprocessor.normalize(image)
            img_feat = self.image_preprocessor.extract_features(normalized)

        if text is not None:
            txt_tok = self.tokenizer.tokenize(text)

        return Sample(
            id=sample_id,
            image_features=img_feat,
            text_tokens=txt_tok,
            targets=targets,
        )

    def create_sample_list(self, samples: List[Sample]) -> SampleList:
        """Create a SampleList from a list of Samples."""
        return SampleList(samples)

    # --- Encoding ---

    def encode_image(self, features: np.ndarray) -> np.ndarray:
        """Encode image features. (batch, regions, feat_dim) -> (batch, embed_dim)."""
        encoded = self.image_encoder.encode(features)
        # Pool across regions
        return np.mean(encoded, axis=-2) if encoded.ndim == 3 else encoded

    def encode_text(self, tokens: np.ndarray) -> np.ndarray:
        """Encode text tokens. (batch, seq_len) -> (batch, embed_dim)."""
        encoded = self.text_encoder.encode(tokens)
        # Pool across sequence
        return np.mean(encoded, axis=1)

    # --- Fusion ---

    def fuse(self, image_feat: np.ndarray, text_feat: np.ndarray) -> np.ndarray:
        """Fuse image and text features."""
        if self.fusion_type == FusionType.ATTENTION:
            # Need sequence representations for attention
            img = image_feat[:, None, :] if image_feat.ndim == 2 else image_feat
            txt = text_feat[:, None, :] if text_feat.ndim == 2 else text_feat
            attended = self.fusion.fuse(txt, img)
            return np.mean(attended, axis=1) if attended.ndim == 3 else attended
        return self.fusion.fuse(image_feat, text_feat)

    # --- VQA Pipeline ---

    def vqa_predict(self, image_features: np.ndarray,
                    text_tokens: np.ndarray) -> np.ndarray:
        """
        Full VQA pipeline: encode → fuse → predict.

        Args:
            image_features: (batch, regions, feat_dim) or (batch, feat_dim)
            text_tokens: (batch, seq_len)

        Returns:
            logits: (batch, num_answers)
        """
        img_enc = self.encode_image(image_features)
        txt_enc = self.encode_text(text_tokens)
        fused = self.fuse(img_enc, txt_enc)
        return self.vqa_head.forward(fused)

    def vqa_loss(self, logits: np.ndarray, targets: np.ndarray) -> float:
        """Compute VQA loss (binary CE for soft targets)."""
        return binary_cross_entropy(logits, targets)

    # --- Captioning Pipeline ---

    def caption_predict(self, image_features: np.ndarray,
                        temperature: float = 1.0) -> np.ndarray:
        """
        Generate captions from image features.

        Args:
            image_features: (batch, regions, feat_dim)

        Returns:
            tokens: (batch, max_caption_len)
        """
        img_enc = self.encode_image(image_features)
        return self.caption_head.generate(img_enc, temperature)

    # --- Metrics ---

    def compute_vqa_accuracy(self, predictions: np.ndarray,
                             targets: np.ndarray) -> float:
        """Compute VQA accuracy."""
        return vqa_accuracy(predictions, targets)

    def compute_bleu(self, reference: np.ndarray,
                     hypothesis: np.ndarray, max_n: int = 4) -> float:
        """Compute BLEU score."""
        return bleu_score(reference, hypothesis, max_n)

    def compute_cider(self, reference: np.ndarray,
                      hypothesis: np.ndarray) -> float:
        """Compute approximate CIDEr score."""
        return cider_score_approx(reference, hypothesis)

    # --- Registry access ---

    def register_component(self, category: str, name: str, obj: Any) -> Result:
        """Register a custom component."""
        return self.registry.register(category, name, obj)

    def get_component(self, category: str, name: str) -> Result:
        """Retrieve a registered component."""
        return self.registry.get(category, name)

    # --- Health ---

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniMMFEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "embed_dim": self.embed_dim,
            "vocab_size": self.vocab_size,
            "num_answers": self.num_answers,
            "fusion_type": self.fusion_type.value,
            "registry_categories": self.registry.categories(),
            "registered_encoders": self.registry.list_registered("encoder"),
            "registered_metrics": self.registry.list_registered("metric"),
            "registered_fusions": self.registry.list_registered("fusion"),
            "components": [
                "Registry", "ImageEncoder", "TextEncoder",
                "ConcatFusion", "ElementWiseFusion", "BilinearFusion",
                "AttentionFusion", "VQAHead", "CaptionHead",
                "TextTokenizer", "ImagePreprocessor",
            ],
            "tasks": ["vqa", "captioning"],
            "metrics": ["vqa_accuracy", "bleu", "cider"],
            "status": "operational",
        }
