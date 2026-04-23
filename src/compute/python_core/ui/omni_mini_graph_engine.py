ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI MINI GRAPH ENGINE — IoT/Smart Home Sensor Data Visualization
# ===========================================================================
# Source Paradigm: https://github.com/kalkih/mini-graph-card
# Domain Layer  : UI (Data Visualization)
# Zero-Prod     : 100% Native — json, os, math, real SVG generation
# ===========================================================================
"""
mini-graph-card teaches us:
  1. Minimalistic sensor data visualization (line, bar, area)
  2. Threshold-based color transitions
  3. Multi-entity overlay graphs
  4. Data aggregation with timeframe control
  5. SVG-based rendering (lightweight, no canvas dependency)
  6. Home Assistant integration pattern

This engine distills those paradigms into OMNI-native Python SVG
graph generator for real-time sensor/metric data visualization.
"""

import json
import math
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class DataPoint:
    timestamp: float
    value: float
    label: str = ""


@dataclass
class GraphEntity:
    name: str
    data: List[DataPoint] = field(default_factory=list)
    color: str = "#4FC3F7"
    line_width: float = 2.0
    show_fill: bool = True
    fill_opacity: float = 0.15


@dataclass
class Threshold:
    value: float
    color: str


@dataclass
class GraphConfig:
    title: str = ""
    width: int = 500
    height: int = 200
    show_labels: bool = True
    show_legend: bool = True
    show_grid: bool = True
    line_smoothing: bool = True
    thresholds: List[Threshold] = field(default_factory=list)
    background_color: str = "#1e1e2e"
    text_color: str = "#cdd6f4"
    grid_color: str = "#313244"
    font_family: str = "Inter, sans-serif"


# ── SVG Graph Renderer ─────────────────────────────────────────────────────

class SVGRenderer:
    """Generate SVG graphs from data points — zero external dependencies."""

    PADDING = {"top": 30, "right": 20, "bottom": 30, "left": 50}

    @staticmethod
    def render_line_graph(entities: List[GraphEntity],
                           config: GraphConfig) -> str:
        """Render a full SVG line graph with axes and legend."""
        p = SVGRenderer.PADDING
        plot_w = config.width - p["left"] - p["right"]
        plot_h = config.height - p["top"] - p["bottom"]

        # Compute global min/max
        all_values = [dp.value for e in entities for dp in e.data if e.data]
        if not all_values:
            all_values = [0, 1]
        v_min = min(all_values)
        v_max = max(all_values)
        if v_min == v_max:
            v_min -= 1
            v_max += 1
        v_range = v_max - v_min

        all_times = [dp.timestamp for e in entities for dp in e.data if e.data]
        t_min = min(all_times) if all_times else 0
        t_max = max(all_times) if all_times else 1
        t_range = t_max - t_min or 1

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{config.width}" height="{config.height}" '
            f'viewBox="0 0 {config.width} {config.height}" '
            f'style="background:{config.background_color};border-radius:8px;font-family:{config.font_family}">',
        ]

        # Title
        if config.title:
            svg_parts.append(
                f'<text x="{p["left"]}" y="18" fill="{config.text_color}" font-size="13" font-weight="600">{config.title}</text>'
            )

        # Grid lines
        if config.show_grid:
            for i in range(5):
                y = p["top"] + (plot_h * i / 4)
                svg_parts.append(
                    f'<line x1="{p["left"]}" y1="{y:.1f}" x2="{p["left"] + plot_w}" y2="{y:.1f}" '
                    f'stroke="{config.grid_color}" stroke-width="0.5"/>'
                )

        # Y-axis labels
        if config.show_labels:
            for i in range(5):
                y = p["top"] + (plot_h * i / 4)
                val = v_max - (v_range * i / 4)
                svg_parts.append(
                    f'<text x="{p["left"] - 5}" y="{y + 4:.1f}" fill="{config.text_color}" '
                    f'font-size="9" text-anchor="end">{val:.1f}</text>'
                )

        # Threshold lines
        for thresh in config.thresholds:
            if v_min <= thresh.value <= v_max:
                ty = p["top"] + plot_h - ((thresh.value - v_min) / v_range * plot_h)
                svg_parts.append(
                    f'<line x1="{p["left"]}" y1="{ty:.1f}" x2="{p["left"] + plot_w}" y2="{ty:.1f}" '
                    f'stroke="{thresh.color}" stroke-width="1" stroke-dasharray="4,3" opacity="0.7"/>'
                )

        # Data lines
        for entity in entities:
            if not entity.data:
                continue

            sorted_data = sorted(entity.data, key=lambda d: d.timestamp)
            points = []
            for dp in sorted_data:
                x = p["left"] + ((dp.timestamp - t_min) / t_range * plot_w)
                y = p["top"] + plot_h - ((dp.value - v_min) / v_range * plot_h)
                points.append((x, y))

            if len(points) < 2:
                continue

            # Build path
            if config.line_smoothing and len(points) > 2:
                path_d = SVGRenderer._smooth_path(points)
            else:
                path_d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
                for x, y in points[1:]:
                    path_d += f" L{x:.1f},{y:.1f}"

            svg_parts.append(
                f'<path d="{path_d}" fill="none" stroke="{entity.color}" '
                f'stroke-width="{entity.line_width}" stroke-linecap="round" stroke-linejoin="round"/>'
            )

            # Fill area
            if entity.show_fill:
                baseline = p["top"] + plot_h
                fill_d = path_d + f" L{points[-1][0]:.1f},{baseline:.1f} L{points[0][0]:.1f},{baseline:.1f} Z"
                svg_parts.append(
                    f'<path d="{fill_d}" fill="{entity.color}" opacity="{entity.fill_opacity}"/>'
                )

        # Legend
        if config.show_legend and len(entities) > 1:
            lx = p["left"]
            ly = config.height - 8
            for i, e in enumerate(entities):
                offset = i * 100
                svg_parts.append(
                    f'<rect x="{lx + offset}" y="{ly - 6}" width="10" height="10" rx="2" fill="{e.color}"/>'
                )
                svg_parts.append(
                    f'<text x="{lx + offset + 14}" y="{ly + 3}" fill="{config.text_color}" font-size="9">{e.name}</text>'
                )

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    @staticmethod
    def _smooth_path(points: List[Tuple[float, float]]) -> str:
        """Create a smooth bezier curve through points."""
        d = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
        for i in range(1, len(points)):
            x0, y0 = points[i - 1]
            x1, y1 = points[i]
            mx = (x0 + x1) / 2
            d += f" C{mx:.1f},{y0:.1f} {mx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
        return d

    @staticmethod
    def render_bar_graph(entity: GraphEntity, config: GraphConfig) -> str:
        """Render a simple bar chart SVG."""
        p = SVGRenderer.PADDING
        plot_w = config.width - p["left"] - p["right"]
        plot_h = config.height - p["top"] - p["bottom"]

        if not entity.data:
            return '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"><text x="10" y="30">No data</text></svg>'

        values = [dp.value for dp in entity.data]
        v_max = max(values) if values else 1
        bar_count = len(values)
        bar_width = max(2, plot_w / bar_count - 2)

        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{config.width}" height="{config.height}" '
               f'style="background:{config.background_color};border-radius:8px;font-family:{config.font_family}">']

        if config.title:
            svg.append(f'<text x="{p["left"]}" y="18" fill="{config.text_color}" font-size="13" font-weight="600">{config.title}</text>')

        for i, dp in enumerate(entity.data):
            bh = (dp.value / v_max) * plot_h if v_max > 0 else 0
            x = p["left"] + i * (plot_w / bar_count)
            y = p["top"] + plot_h - bh

            # Threshold color
            color = entity.color
            for thresh in sorted(config.thresholds, key=lambda t: t.value, reverse=True):
                if dp.value >= thresh.value:
                    color = thresh.color
                    break

            svg.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bh:.1f}" '
                f'rx="2" fill="{color}" opacity="0.85"/>'
            )

        svg.append("</svg>")
        return "\n".join(svg)


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniMiniGraphEngine:
    """
    OMNI Mini Graph Engine — Zero-Prod SVG Data Visualization.

    Capabilities (all native — pure Python math + string SVG):
      - Line graph with bezier smoothing
      - Bar chart with threshold colors
      - Multi-entity overlay graphs
      - Configurable axes, grid, legend
      - SVG file export (no canvas/DOM needed)
      - Threshold-based color transitions
    """

    def __init__(self):
        self.renderer = SVGRenderer()

    def line_graph(self, entities: List[GraphEntity],
                    config: Optional[GraphConfig] = None) -> str:
        if config is None:
            config = GraphConfig()
        return self.renderer.render_line_graph(entities, config)

    def bar_graph(self, entity: GraphEntity,
                   config: Optional[GraphConfig] = None) -> str:
        if config is None:
            config = GraphConfig()
        return self.renderer.render_bar_graph(entity, config)

    def save_svg(self, svg_content: str, filepath: str) -> Dict:
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return {"saved": filepath, "size_bytes": os.path.getsize(filepath)}

    def demo_graph(self) -> str:
        """Generate a demo temperature graph with sample data."""
        now = time.time()
        data = [DataPoint(timestamp=now - (23 - i) * 3600, value=20 + 5 * math.sin(i / 3.5) + (i % 3))
                for i in range(24)]
        entity = GraphEntity(name="Temperature °C", data=data, color="#f38ba8")
        config = GraphConfig(
            title="Temperature (24h)",
            thresholds=[Threshold(value=25, color="#fab387"), Threshold(value=28, color="#f38ba8")],
        )
        return self.renderer.render_line_graph([entity], config)

    def diagnostics(self) -> Dict:
        return {
            "engine": "OmniMiniGraphEngine",
            "status": "active",
            "capabilities": ["line_graph", "bar_graph", "bezier_smooth",
                             "threshold_colors", "multi_entity", "svg_export"],
        }


if __name__ == "__main__":
    engine = OmniMiniGraphEngine()
    svg = engine.demo_graph()
    engine.save_svg(svg, os.path.join(os.path.dirname(__file__), "..", ".demo_graph.svg"))
    print(f"[MiniGraph] Demo SVG generated ({len(svg)} bytes)")
    print(json.dumps(engine.diagnostics(), indent=2))
