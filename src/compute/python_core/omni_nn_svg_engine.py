"""
OMNI NN-SVG Engine — Production Hard-Code

Generates real SVG markup for neural network architecture diagrams
programmatically, replicating the core logic of alexlenail/NN-SVG.
Produces valid, renderable SVG strings for fully-connected (FCNN),
convolutional (LeNet-style), and custom layer architectures.

No external JS/browser dependency — pure Python SVG generation using
actual geometric calculations for node positions, edges, and labels.

References:
    - https://github.com/alexlenail/NN-SVG
    - SVG 1.1 specification for rect/circle/line/text elements
"""

import asyncio
import logging
import math
import time
import uuid
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple



ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err

def _generate_fcnn_svg(
    layer_sizes: List[int],
    canvas_width: int = 800,
    canvas_height: int = 600,
    node_radius: int = 14,
    node_color: str = "#4A90D9",
    edge_color: str = "#CCCCCC",
    font_size: int = 11,
) -> str:
    """
    Generates a real SVG string for a fully-connected neural network.

    Args:
        layer_sizes: List of neuron counts per layer, e.g. [784, 128, 64, 10].
        canvas_width: Width of the SVG canvas in pixels.
        canvas_height: Height of the SVG canvas in pixels.
        node_radius: Radius of each neuron circle.
        node_color: Fill color for neuron circles.
        edge_color: Stroke color for connection lines.
        font_size: Font size for layer labels.

    Returns:
        A valid SVG XML string.
    """
    num_layers = len(layer_sizes)
    h_spacing = canvas_width / (num_layers + 1)

    svg = ET.Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        width=str(canvas_width),
        height=str(canvas_height),
        viewBox=f"0 0 {canvas_width} {canvas_height}",
    )

    # Background
    ET.SubElement(
        svg, "rect",
        width=str(canvas_width), height=str(canvas_height),
        fill="#1a1a2e", rx="8",
    )

    # Compute node positions
    positions: List[List[Tuple[float, float]]] = []
    for li, size in enumerate(layer_sizes):
        cx = h_spacing * (li + 1)
        # Cap display neurons at 10 for readability
        display_size = min(size, 10)
        v_spacing = canvas_height / (display_size + 1)
        layer_pos = []
        for ni in range(display_size):
            cy = v_spacing * (ni + 1)
            layer_pos.append((cx, cy))
        positions.append(layer_pos)

    # Draw edges between consecutive layers
    for li in range(num_layers - 1):
        for x1, y1 in positions[li]:
            for x2, y2 in positions[li + 1]:
                ET.SubElement(
                    svg, "line",
                    x1=str(x1), y1=str(y1),
                    x2=str(x2), y2=str(y2),
                    stroke=edge_color,
                    **{"stroke-width": "0.5", "stroke-opacity": "0.4"},
                )

    # Draw nodes
    for li, layer_pos in enumerate(positions):
        for cx, cy in layer_pos:
            ET.SubElement(
                svg, "circle",
                cx=str(cx), cy=str(cy), r=str(node_radius),
                fill=node_color, stroke="#FFFFFF",
                **{"stroke-width": "1.5"},
            )

    # Draw layer labels
    for li, size in enumerate(layer_sizes):
        cx = h_spacing * (li + 1)
        label = ET.SubElement(
            svg, "text",
            x=str(cx), y=str(canvas_height - 15),
            fill="#FFFFFF",
            **{
                "text-anchor": "middle",
                "font-family": "monospace",
                "font-size": str(font_size),
            },
        )
        label.text = f"Layer {li} ({size})"

    return ET.tostring(svg, encoding="unicode")


def _generate_conv_svg(
    channels: List[int],
    canvas_width: int = 900,
    canvas_height: int = 400,
) -> str:
    """
    Generates a real SVG string for a convolutional network (LeNet-style).

    Args:
        channels: List of channel counts per conv layer, e.g. [1, 6, 16].
        canvas_width: Width of the SVG canvas.
        canvas_height: Height of the SVG canvas.

    Returns:
        A valid SVG XML string.
    """
    num_layers = len(channels)
    h_spacing = canvas_width / (num_layers + 1)
    max_ch = max(channels)

    svg = ET.Element(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        width=str(canvas_width),
        height=str(canvas_height),
        viewBox=f"0 0 {canvas_width} {canvas_height}",
    )

    ET.SubElement(
        svg, "rect",
        width=str(canvas_width), height=str(canvas_height),
        fill="#0f3460", rx="8",
    )

    colors = ["#e94560", "#16213e", "#533483", "#0f3460", "#e94560"]

    for li, ch in enumerate(channels):
        cx = h_spacing * (li + 1)
        # Height proportional to channel count
        rect_h = max(30, int((ch / max(max_ch, 1)) * (canvas_height * 0.6)))
        rect_w = max(20, 60 - li * 8)
        ry = (canvas_height - rect_h) / 2

        color = colors[li % len(colors)]
        ET.SubElement(
            svg, "rect",
            x=str(cx - rect_w / 2), y=str(ry),
            width=str(rect_w), height=str(rect_h),
            fill=color, stroke="#FFFFFF",
            rx="4",
            **{"stroke-width": "1"},
        )

        label = ET.SubElement(
            svg, "text",
            x=str(cx), y=str(canvas_height - 20),
            fill="#FFFFFF",
            **{
                "text-anchor": "middle",
                "font-family": "monospace",
                "font-size": "11",
            },
        )
        label.text = f"Conv {li} ({ch}ch)"

        # Draw connection arrows between layers
        if li > 0:
            prev_cx = h_spacing * li
            ET.SubElement(
                svg, "line",
                x1=str(prev_cx + 30), y1=str(canvas_height / 2),
                x2=str(cx - rect_w / 2), y2=str(canvas_height / 2),
                stroke="#FFFFFF",
                **{"stroke-width": "1.5", "stroke-opacity": "0.6"},
            )

    return ET.tostring(svg, encoding="unicode")


class OmniNnSvgEngine:
    """
    Omni NN-SVG Engine (Production Hard-Code).

    Generates real, valid SVG markup for neural network architecture
    diagrams. Supports fully-connected (FCNN) and convolutional (CNN)
    architectures. All geometry is computed natively in Python.

    Attributes:
        config: Engine configuration dictionary.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes the NN-SVG engine.

        Args:
            config: Optional configuration overrides.
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_active: bool = False
        self._engine_id: str = str(uuid.uuid4())
        self._start_time: float = 0.0

    async def initialize(self) -> Dict[str, Any]:
        """
        Monadic initialization — smoke-tests SVG generation.

        Returns:
            Dict with status, engine_id, and message.
        """
        try:
            self.logger.info(
                f"[{self.__class__.__name__}] Validating native SVG generation..."
            )

            # Smoke-test: generate a small FCNN SVG
            svg_out = _generate_fcnn_svg([2, 3, 1])
            assert "<svg" in svg_out, "SVG output missing root element"
            assert "<circle" in svg_out, "SVG output missing neuron nodes"
            assert "<line" in svg_out, "SVG output missing connection edges"

            self._is_active = True
            self._start_time = time.time()
            return {
                "status": "success",
                "engine_id": self._engine_id,
                "message": "NN-SVG engine initialized — native SVG generation ready.",
            }
        except Exception as e:
            self.logger.error(f"Initialization failure: {e}")
            return {"status": "error", "engine_id": self._engine_id, "error": str(e)}

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receives parameters and generates real SVG markup.

        Args:
            data: Contains 'architecture' ('fcnn' or 'cnn') and 'layers'.

        Returns:
            Monadic result dict with SVG string and metadata.
        """
        if not self._is_active:
            return {
                "status": "error",
                "engine_id": self._engine_id,
                "error": "Engine inactive.",
            }

        try:
            st = time.time()
            arch = data.get("architecture", "fcnn").lower()
            layers = data.get("layers", [784, 256, 128, 10])

            if not layers or len(layers) < 2:
                raise ValueError("Must specify at least 2 layers.")

            if arch == "cnn":
                svg_str = _generate_conv_svg(channels=layers)
            else:
                svg_str = _generate_fcnn_svg(layer_sizes=layers)

            calc_time_ms = (time.time() - st) * 1000.0

            # Count generated SVG elements
            root = ET.fromstring(svg_str)
            num_circles = len(root.findall(".//{http://www.w3.org/2000/svg}circle"))
            num_lines = len(root.findall(".//{http://www.w3.org/2000/svg}line"))
            num_rects = len(root.findall(".//{http://www.w3.org/2000/svg}rect"))
            # Fallback: count without namespace (ElementTree quirk)
            if num_circles == 0:
                num_circles = len(root.findall(".//circle"))
            if num_lines == 0:
                num_lines = len(root.findall(".//line"))
            if num_rects == 0:
                num_rects = len(root.findall(".//rect"))

            return {
                "status": "success",
                "data": {
                    "nn_svg_result": {
                        "architecture": arch,
                        "layers": layers,
                        "svg_length_bytes": len(svg_str.encode("utf-8")),
                        "svg_element_counts": {
                            "circles": num_circles,
                            "lines": num_lines,
                            "rects": num_rects,
                        },
                        "svg_valid": svg_str.startswith("<svg"),
                        "execution_time_ms": round(calc_time_ms, 2),
                    },
                    "svg_markup": svg_str,
                },
            }
        except Exception as e:
            self.logger.error(f"NN-SVG execution error: {e}")
            return {"status": "error", "engine_id": self._engine_id, "error": str(e)}

    def diagnostics(self) -> Dict[str, Any]:
        """
        Returns engine health diagnostics.

        Returns:
            Dict with engine status and uptime.
        """
        return {
            "engine": self.__class__.__name__,
            "engine_id": self._engine_id,
            "status": "active" if self._is_active else "inactive",
            "uptime_seconds": (
                round(time.time() - self._start_time, 2) if self._is_active else 0.0
            ),
            "supported_architectures": ["fcnn", "cnn"],
        }
