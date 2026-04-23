"""OmniMatplotlibFigureCanvasEngine — Production-grade figure layout and canvas geometry engine.

Computes subplot grid layouts, axis coordinate mappings, figure DPI scaling,
and bounding-box collision detection for figure composition. No rendering —
pure computational geometry for canvas planning.
"""
import math
from typing import Any, Dict, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniMatplotlibFigureCanvasEngine:
    """Production engine for figure canvas layout geometry computation."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, dpi: int = 100, default_fig_width: float = 10.0, default_fig_height: float = 8.0):
        """
        Initialize canvas engine.

        Args:
            dpi: Dots per inch for pixel conversion.
            default_fig_width: Default figure width in inches.
            default_fig_height: Default figure height in inches.
        """
        if dpi <= 0:
            raise ValueError("dpi must be positive.")
        self.dpi = dpi
        self.default_fig_width = default_fig_width
        self.default_fig_height = default_fig_height

    def compute_subplot_grid(
        self, n_rows: int, n_cols: int, padding: float = 0.05, fig_width: float = None, fig_height: float = None
    ) -> Result:
        """
        Compute subplot bounding boxes for an n_rows × n_cols grid layout.

        Each subplot is described by (x, y, width, height) in normalized
        figure coordinates [0, 1]. Padding is applied between subplots.

        Args:
            n_rows: Number of rows in the grid.
            n_cols: Number of columns in the grid.
            padding: Fractional padding between subplots (0–0.5).
            fig_width: Figure width in inches (uses default if None).
            fig_height: Figure height in inches (uses default if None).

        Returns:
            Result with subplot bounding boxes and pixel dimensions.
        """
        try:
            if n_rows <= 0 or n_cols <= 0:
                return Err(ValueError("n_rows and n_cols must be positive."))
            if not 0 <= padding < 0.5:
                return Err(ValueError("padding must be in [0, 0.5)."))

            fw = fig_width or self.default_fig_width
            fh = fig_height or self.default_fig_height

            cell_w = (1.0 - padding * (n_cols + 1)) / n_cols
            cell_h = (1.0 - padding * (n_rows + 1)) / n_rows

            subplots = []
            for row in range(n_rows):
                for col in range(n_cols):
                    x = padding + col * (cell_w + padding)
                    y = 1.0 - padding - (row + 1) * (cell_h + padding) + padding
                    subplots.append({
                        "row": row,
                        "col": col,
                        "index": row * n_cols + col,
                        "bbox_normalized": {
                            "x": round(x, 6),
                            "y": round(y, 6),
                            "width": round(cell_w, 6),
                            "height": round(cell_h, 6),
                        },
                        "bbox_pixels": {
                            "x": round(x * fw * self.dpi, 1),
                            "y": round(y * fh * self.dpi, 1),
                            "width": round(cell_w * fw * self.dpi, 1),
                            "height": round(cell_h * fh * self.dpi, 1),
                        },
                    })

            return Ok({
                "n_rows": n_rows,
                "n_cols": n_cols,
                "total_subplots": n_rows * n_cols,
                "figure_size_inches": {"width": fw, "height": fh},
                "figure_size_pixels": {"width": round(fw * self.dpi), "height": round(fh * self.dpi)},
                "dpi": self.dpi,
                "subplots": subplots,
            })

        except Exception as e:
            return Err(e)

    def compute_axis_ticks(
        self, data_min: float, data_max: float, n_ticks: int = 5
    ) -> Result:
        """
        Compute evenly spaced axis tick positions using Wilkinson's extended algorithm concept.

        Args:
            data_min: Minimum data value.
            data_max: Maximum data value.
            n_ticks: Desired number of ticks.

        Returns:
            Result with tick positions and step size.
        """
        try:
            if data_min >= data_max:
                return Err(ValueError("data_min must be less than data_max."))
            if n_ticks < 2:
                return Err(ValueError("n_ticks must be at least 2."))

            data_range = data_max - data_min
            raw_step = data_range / (n_ticks - 1)

            # Round step to a "nice" number
            magnitude = math.floor(math.log10(raw_step))
            residual = raw_step / (10 ** magnitude)

            if residual <= 1.5:
                nice_step = 1.0
            elif residual <= 3.0:
                nice_step = 2.0
            elif residual <= 7.0:
                nice_step = 5.0
            else:
                nice_step = 10.0

            step = nice_step * (10 ** magnitude)
            tick_start = math.floor(data_min / step) * step
            ticks = []
            t = tick_start
            while t <= data_max + step * 0.01:
                ticks.append(round(t, 10))
                t += step

            return Ok({
                "ticks": ticks,
                "step": step,
                "n_ticks_generated": len(ticks),
                "data_range": round(data_range, 10),
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniMatplotlibFigureCanvasEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "dpi": self.dpi,
            "complexity": "O(rows * cols) subplot grid layout computation",
        }
