"""
OmniGluoncvEngine — Native Computer Vision Model Zoo & Toolkit.

Studied from: dmlc/gluon-cv (5.9k★)
Implements: Convolutional building blocks (Conv2D, pooling, batch norm),
residual network (ResNet) architecture builder, object detection utilities
(anchor boxes, IoU, NMS), image preprocessing pipeline, and model zoo
registry for vision architectures.

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Zero external dependencies.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniGluoncvEngine"

# Type alias
Tensor2D = List[List[float]]
Tensor3D = List[Tensor2D]       # [channels, height, width]
Tensor4D = List[Tensor3D]       # [batch, channels, height, width]
BBox = Tuple[float, float, float, float]  # (x1, y1, x2, y2)


# ---------------------------------------------------------------------------
# Activation functions
# ---------------------------------------------------------------------------

class Activations:
    """Neural network activation functions."""

    @staticmethod
    def relu(x: float) -> float:
        """Execute relu operation for Activations."""
        return max(0.0, x)

    @staticmethod
    def sigmoid(x: float) -> float:
        """Execute sigmoid operation for Activations."""
        x = max(min(x, 500.0), -500.0)
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def leaky_relu(x: float, alpha: float = 0.1) -> float:
        """Execute leaky relu operation for Activations."""
        return x if x >= 0 else alpha * x


# ---------------------------------------------------------------------------
# Tensor utilities
# ---------------------------------------------------------------------------

class TensorOps:
    """Lightweight tensor operations for vision pipelines."""

    @staticmethod
    def zeros_2d(h: int, w: int) -> Tensor2D:
        """Execute zeros 2d operation for TensorOps."""
        return [[0.0 for _ in range(w)] for _ in range(h)]

    @staticmethod
    def zeros_3d(c: int, h: int, w: int) -> Tensor3D:
        """Execute zeros 3d operation for TensorOps."""
        return [TensorOps.zeros_2d(h, w) for _ in range(c)]

    @staticmethod
    def apply_2d(
        tensor: Tensor2D, fn: Callable[[float], float]
    ) -> Tensor2D:
        """Apply element-wise function to a 2D tensor."""
        return [[fn(tensor[r][c]) for c in range(len(tensor[0]))] for r in range(len(tensor))]


# ---------------------------------------------------------------------------
# Convolutional building blocks
# ---------------------------------------------------------------------------

class Conv2D:
    """2D convolution layer with native implementation.

    Attributes:
        in_channels: Number of input channels.
        out_channels: Number of output channels.
        kernel_size: Spatial dimension of kernel.
        stride: Convolution stride.
        padding: Zero-padding on each side.
        weights: Learnable filter weights [out_c, in_c, kh, kw].
        bias: Learnable bias per output channel.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        padding: int = 0,
    ) -> None:
        """Initialize Conv2D."""
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

        # Xavier init
        fan_in = in_channels * kernel_size * kernel_size
        fan_out = out_channels * kernel_size * kernel_size
        limit = math.sqrt(6.0 / (fan_in + fan_out))

        self.weights: List[Tensor3D] = [
            [
                [[random.uniform(-limit, limit) for _ in range(kernel_size)]
                 for _ in range(kernel_size)]
                for _ in range(in_channels)
            ]
            for _ in range(out_channels)
        ]
        self.bias: List[float] = [0.0 for _ in range(out_channels)]

    def forward(self, x: Tensor3D) -> Tensor3D:
        """Forward pass of Conv2D.

        Args:
            x: Input tensor [in_channels, height, width].

        Returns:
            Output tensor [out_channels, out_h, out_w].
        """
        c_in, h_in, w_in = len(x), len(x[0]), len(x[0][0])
        h_out = (h_in + 2 * self.padding - self.kernel_size) // self.stride + 1
        w_out = (w_in + 2 * self.padding - self.kernel_size) // self.stride + 1

        # Pad input
        if self.padding > 0:
            padded = TensorOps.zeros_3d(c_in, h_in + 2 * self.padding, w_in + 2 * self.padding)
            for c in range(c_in):
                for r in range(h_in):
                    for col in range(w_in):
                        padded[c][r + self.padding][col + self.padding] = x[c][r][col]
        else:
            padded = x

        output = TensorOps.zeros_3d(self.out_channels, h_out, w_out)

        for oc in range(self.out_channels):
            for oh in range(h_out):
                for ow in range(w_out):
                    val = self.bias[oc]
                    for ic in range(c_in):
                        for kh in range(self.kernel_size):
                            for kw in range(self.kernel_size):
                                ih = oh * self.stride + kh
                                iw = ow * self.stride + kw
                                val += padded[ic][ih][iw] * self.weights[oc][ic][kh][kw]
                    output[oc][oh][ow] = val

        return output


class MaxPool2D:
    """2D max pooling layer."""

    def __init__(self, kernel_size: int = 2, stride: int = 2) -> None:
        """Initialize MaxPool2D."""
        self.kernel_size = kernel_size
        self.stride = stride

    def forward(self, x: Tensor3D) -> Tensor3D:
        """Forward pass.

        Args:
            x: Input tensor [channels, height, width].

        Returns:
            Pooled tensor.
        """
        c, h, w = len(x), len(x[0]), len(x[0][0])
        h_out = (h - self.kernel_size) // self.stride + 1
        w_out = (w - self.kernel_size) // self.stride + 1
        output = TensorOps.zeros_3d(c, h_out, w_out)

        for ch in range(c):
            for oh in range(h_out):
                for ow in range(w_out):
                    max_val = float("-inf")
                    for kh in range(self.kernel_size):
                        for kw in range(self.kernel_size):
                            val = x[ch][oh * self.stride + kh][ow * self.stride + kw]
                            if val > max_val:
                                max_val = val
                    output[ch][oh][ow] = max_val

        return output


class BatchNorm2D:
    """Batch normalization for 2D feature maps (per-channel).

    Uses running statistics for inference mode.
    """

    def __init__(self, num_features: int, eps: float = 1e-5, momentum: float = 0.1) -> None:
        """Initialize BatchNorm2D."""
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.gamma: List[float] = [1.0] * num_features
        self.beta: List[float] = [0.0 for _ in range(num_features)]
        self.running_mean: List[float] = [0.0 for _ in range(num_features)]
        self.running_var: List[float] = [1.0] * num_features

    def forward(self, x: Tensor3D, training: bool = False) -> Tensor3D:
        """Forward pass.

        Args:
            x: Input tensor [channels, height, width].
            training: If True, compute batch stats; otherwise use running stats.

        Returns:
            Normalized tensor.
        """
        c, h, w = len(x), len(x[0]), len(x[0][0])
        output = TensorOps.zeros_3d(c, h, w)

        for ch in range(c):
            if training:
                vals = [x[ch][r][col] for r in range(h) for col in range(w)]
                mean = sum(vals) / len(vals)
                var = sum((v - mean) ** 2 for v in vals) / len(vals)
                self.running_mean[ch] = (
                    (1 - self.momentum) * self.running_mean[ch] + self.momentum * mean
                )
                self.running_var[ch] = (
                    (1 - self.momentum) * self.running_var[ch] + self.momentum * var
                )
            else:
                mean = self.running_mean[ch]
                var = self.running_var[ch]

            inv_std = 1.0 / math.sqrt(var + self.eps)
            for r in range(h):
                for col in range(w):
                    output[ch][r][col] = (
                        self.gamma[ch] * (x[ch][r][col] - mean) * inv_std + self.beta[ch]
                    )

        return output


# ---------------------------------------------------------------------------
# ResNet architecture builder
# ---------------------------------------------------------------------------

@dataclass
class ResidualBlock:
    """A single residual block with skip connection.

    Contains two Conv2D layers with batch norm and ReLU activation.
    """
    conv1: Conv2D
    bn1: BatchNorm2D
    conv2: Conv2D
    bn2: BatchNorm2D
    channels: int

    def forward(self, x: Tensor3D) -> Tensor3D:
        """Forward pass with residual skip connection.

        Args:
            x: Input tensor.

        Returns:
            Output with skip connection added.
        """
        identity = x
        out = self.conv1.forward(x)
        out = self.bn1.forward(out)
        out = [[
            [Activations.relu(out[c][r][col]) for col in range(len(out[0][0]))]
            for r in range(len(out[0]))]
            for c in range(len(out))
        ]
        out = self.conv2.forward(out)
        out = self.bn2.forward(out)

        # Add skip connection (only if dimensions match)
        if len(identity) == len(out) and len(identity[0]) == len(out[0]):
            for c in range(len(out)):
                for r in range(len(out[0])):
                    for col in range(len(out[0][0])):
                        out[c][r][col] += identity[c][r][col]

        # ReLU after addition
        out = [[
            [Activations.relu(out[c][r][col]) for col in range(len(out[0][0]))]
            for r in range(len(out[0]))]
            for c in range(len(out))
        ]
        return out


class ResNetBuilder:
    """Builder for ResNet-style architectures (ResNet-18/34/50).

    Studied from gluon-cv's model_zoo.resnetv1b implementation.
    """

    @staticmethod
    def build_block(channels: int) -> ResidualBlock:
        """Build a single residual block.

        Args:
            channels: Number of channels.

        Returns:
            ResidualBlock instance.
        """
        return ResidualBlock(
            conv1=Conv2D(channels, channels, kernel_size=3, stride=1, padding=1),
            bn1=BatchNorm2D(channels),
            conv2=Conv2D(channels, channels, kernel_size=3, stride=1, padding=1),
            bn2=BatchNorm2D(channels),
            channels=channels,
        )

    @staticmethod
    def build_stage(channels: int, num_blocks: int) -> List[ResidualBlock]:
        """Build a stage of ResNet blocks.

        Args:
            channels: Channel count for this stage.
            num_blocks: Number of residual blocks.

        Returns:
            List of residual blocks.
        """
        return [ResNetBuilder.build_block(channels) for _ in range(num_blocks)]

    @staticmethod
    def resnet18_config() -> Dict[str, List[int]]:
        """ResNet-18 layer configuration.

        Returns:
            Channel and block count for each stage.
        """
        return {
            "channels": [64, 128, 256, 512],
            "blocks": [2, 2, 2, 2],
        }

    @staticmethod
    def resnet50_config() -> Dict[str, List[int]]:
        """ResNet-50 layer configuration.

        Returns:
            Channel and block count for each stage.
        """
        return {
            "channels": [64, 128, 256, 512],
            "blocks": [3, 4, 6, 3],
        }


# ---------------------------------------------------------------------------
# Object detection utilities — from gluon-cv detection/ssd
# ---------------------------------------------------------------------------

class DetectionUtils:
    """Object detection utilities (anchor boxes, IoU, NMS)."""

    @staticmethod
    def compute_iou(box_a: BBox, box_b: BBox) -> float:
        """Compute Intersection over Union between two bounding boxes.

        Args:
            box_a: (x1, y1, x2, y2) of first box.
            box_b: (x1, y1, x2, y2) of second box.

        Returns:
            IoU score in [0, 1].
        """
        x1 = max(box_a[0], box_b[0])
        y1 = max(box_a[1], box_b[1])
        x2 = min(box_a[2], box_b[2])
        y2 = min(box_a[3], box_b[3])

        inter_area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
        area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
        area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
        union_area = area_a + area_b - inter_area

        if union_area <= 0:
            return 0.0
        return inter_area / union_area

    @staticmethod
    def nms(
        boxes: List[BBox],
        scores: List[float],
        iou_threshold: float = 0.5,
    ) -> List[int]:
        """Non-Maximum Suppression.

        Args:
            boxes: List of bounding boxes.
            scores: Confidence scores for each box.
            iou_threshold: IoU threshold for suppression.

        Returns:
            Indices of kept boxes.
        """
        if not boxes:
            return []

        indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        keep: List[int] = []

        while indices:
            current = indices[0]
            keep.append(current)
            remaining: List[int] = []
            for idx in indices[1:]:
                iou = DetectionUtils.compute_iou(boxes[current], boxes[idx])
                if iou < iou_threshold:
                    remaining.append(idx)
            indices = remaining

        return keep

    @staticmethod
    def generate_anchors(
        feature_map_size: int,
        image_size: int,
        scales: List[float],
        ratios: List[float],
    ) -> List[BBox]:
        """Generate anchor boxes for a feature map.

        Studied from gluon-cv's SSD anchor generator.

        Args:
            feature_map_size: Spatial size of the feature map.
            image_size: Original image spatial size.
            scales: Anchor scales (e.g., [0.1, 0.2, 0.37]).
            ratios: Aspect ratios (e.g., [1.0, 2.0, 0.5]).

        Returns:
            List of anchor boxes in (x1, y1, x2, y2) format.
        """
        anchors: List[BBox] = []
        step = image_size / feature_map_size

        for i in range(feature_map_size):
            for j in range(feature_map_size):
                cx = (j + 0.5) * step
                cy = (i + 0.5) * step

                for scale in scales:
                    for ratio in ratios:
                        w = image_size * scale * math.sqrt(ratio)
                        h = image_size * scale / math.sqrt(ratio)
                        x1 = max(0.0, cx - w / 2)
                        y1 = max(0.0, cy - h / 2)
                        x2 = min(float(image_size), cx + w / 2)
                        y2 = min(float(image_size), cy + h / 2)
                        anchors.append((x1, y1, x2, y2))

        return anchors


# ---------------------------------------------------------------------------
# Image preprocessing pipeline
# ---------------------------------------------------------------------------

class ImagePreprocessor:
    """Image preprocessing pipeline for vision models."""

    @staticmethod
    def normalize_channel(
        channel: Tensor2D, mean: float, std: float
    ) -> Tensor2D:
        """Normalize a single channel: (pixel - mean) / std.

        Args:
            channel: 2D pixel values.
            mean: Channel mean.
            std: Channel standard deviation.

        Returns:
            Normalized channel.
        """
        return [
            [(channel[r][c] - mean) / std for c in range(len(channel[0]))]
            for r in range(len(channel))
        ]

    @staticmethod
    def normalize_imagenet(image: Tensor3D) -> Tensor3D:
        """Normalize image with ImageNet mean/std (per-channel).

        Args:
            image: 3-channel image [C, H, W] with values in [0, 1].

        Returns:
            Normalized image.
        """
        means = [0.485, 0.456, 0.406]
        stds = [0.229, 0.224, 0.225]
        return [
            ImagePreprocessor.normalize_channel(image[c], means[c], stds[c])
            for c in range(min(3, len(image)))
        ]

    @staticmethod
    def random_horizontal_flip(image: Tensor3D, prob: float = 0.5) -> Tensor3D:
        """Randomly flip image horizontally.

        Args:
            image: Input image [C, H, W].
            prob: Probability of flipping.

        Returns:
            Possibly flipped image.
        """
        if random.random() < prob:
            return [
                [row[::-1] for row in channel]
                for channel in image
            ]
        return image


# ---------------------------------------------------------------------------
# Model zoo registry
# ---------------------------------------------------------------------------

class ModelZoo:
    """Registry of available pretrained model architectures.

    Mirrors gluon-cv's model_zoo structure.
    """

    MODELS: Dict[str, Dict[str, object]] = {
        "resnet18_v1": {
            "family": "ResNet", "layers": 18, "top1_acc": 0.709, "params_m": 11.7,
        },
        "resnet50_v1": {
            "family": "ResNet", "layers": 50, "top1_acc": 0.7636, "params_m": 25.6,
        },
        "resnet101_v1": {
            "family": "ResNet", "layers": 101, "top1_acc": 0.7834, "params_m": 44.6,
        },
        "vgg16": {
            "family": "VGG", "layers": 16, "top1_acc": 0.7153, "params_m": 138.0,
        },
        "ssd_512_resnet50": {
            "family": "SSD", "layers": 50, "mAP": 0.317, "params_m": 36.0,
        },
        "yolo3_darknet53": {
            "family": "YOLO", "layers": 53, "mAP": 0.366, "params_m": 61.6,
        },
        "fcn_resnet50_ade": {
            "family": "FCN", "layers": 50, "mIoU": 0.396, "params_m": 39.0,
        },
        "mask_rcnn_resnet50_fpn": {
            "family": "Mask-RCNN", "layers": 50, "mAP": 0.379, "params_m": 44.1,
        },
    }

    @classmethod
    def list_models(cls, family: Optional[str] = None) -> List[str]:
        """List available models, optionally filtered by family.

        Args:
            family: Filter by model family (e.g., "ResNet").

        Returns:
            List of model names.
        """
        if family:
            return [
                name for name, info in cls.MODELS.items()
                if info.get("family") == family
            ]
        return list(cls.MODELS.keys())

    @classmethod
    def get_model_info(cls, name: str) -> Optional[Dict[str, object]]:
        """Get info for a specific model.

        Args:
            name: Model name.

        Returns:
            Model metadata dict or None.
        """
        return cls.MODELS.get(name)


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class OmniGluoncvEngine:
    """Production-grade computer vision model zoo & toolkit engine.

    Capabilities:
        - Conv2D / MaxPool2D / BatchNorm2D building blocks
        - ResNet residual block builder
        - Object detection (IoU, NMS, anchor generation)
        - Image preprocessing (ImageNet normalization, augmentation)
        - Model zoo registry with 8+ architectures
    """

    def __init__(self) -> None:
        """Initialize OmniGluoncvEngine."""
        self.detection = DetectionUtils()
        self.preprocessor = ImagePreprocessor()
        self.model_zoo = ModelZoo()
        self.resnet_builder = ResNetBuilder()
        self._version: str = ENGINE_VERSION
        self._name: str = ENGINE_NAME

    def create_conv2d(
        self, in_c: int, out_c: int, kernel: int = 3,
        stride: int = 1, padding: int = 0
    ) -> Conv2D:
        """Factory method for Conv2D layers.

        Args:
            in_c: Input channels.
            out_c: Output channels.
            kernel: Kernel size.
            stride: Stride.
            padding: Zero-padding.

        Returns:
            Conv2D instance.
        """
        return Conv2D(in_c, out_c, kernel, stride, padding)

    def create_maxpool(self, kernel: int = 2, stride: int = 2) -> MaxPool2D:
        """Factory method for MaxPool2D layers.

        Args:
            kernel: Pooling window size.
            stride: Pooling stride.

        Returns:
            MaxPool2D instance.
        """
        return MaxPool2D(kernel, stride)

    def create_batchnorm(self, features: int) -> BatchNorm2D:
        """Factory method for BatchNorm2D.

        Args:
            features: Number of feature channels.

        Returns:
            BatchNorm2D instance.
        """
        return BatchNorm2D(features)

    def health(self) -> Dict[str, object]:
        """Return engine health diagnostics.

        Returns:
            Dictionary with engine status information.
        """
        return {
            "engine": self._name,
            "version": self._version,
            "status": "operational",
            "model_zoo_count": len(ModelZoo.MODELS),
            "model_families": list({v["family"] for v in ModelZoo.MODELS.values()}),
            "capabilities": [
                "conv2d", "maxpool2d", "batchnorm2d", "resnet_builder",
                "iou", "nms", "anchor_generation", "image_normalization",
                "random_flip", "model_zoo_registry",
            ],
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-gluoncv",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
