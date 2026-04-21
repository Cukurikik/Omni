/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI CHART RENDERER ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : d3.js + Observable Plot + Recharts rendering concepts
// Logic Inherited: TypeScript / UI Layer (Functional Canvas/SVG Chart System)
// Domain Layer   : UI (TypeScript Core)
// ===========================================================================
//
// By studying D3.js's scale/axis/shape pipeline and Recharts' component
// model, Mother learned that charting reduces to a composable pipeline:
//   Data → Scale (domain→range mapping) → Shape (geometry) → Render
//
// TypeScript generic constraints enforce type-safety at each pipeline
// stage. The Scale system uses pure functions (no side effects), making
// charts deterministic and testable without a DOM.

// ---- Scale System (D3-inspired) ----

export interface Scale<D, R> {
  domain: [D, D];
  range: [R, R];
  map(value: D): R;
  invert(value: R): D;
}

export class LinearScale implements Scale<number, number> {
  domain: [number, number];
  range: [number, number];

  constructor(domain: [number, number], range: [number, number]) {
    this.domain = domain;
    this.range = range;
  }

  map(value: number): number {
    const [d0, d1] = this.domain;
    const [r0, r1] = this.range;
    const t = (value - d0) / (d1 - d0);
    return r0 + t * (r1 - r0);
  }

  invert(value: number): number {
    const [d0, d1] = this.domain;
    const [r0, r1] = this.range;
    const t = (value - r0) / (r1 - r0);
    return d0 + t * (d1 - d0);
  }
}

export class LogScale implements Scale<number, number> {
  domain: [number, number];
  range: [number, number];

  constructor(domain: [number, number], range: [number, number]) {
    this.domain = [Math.max(domain[0], 1e-10), domain[1]];
    this.range = range;
  }

  map(value: number): number {
    const logDomain = [Math.log10(this.domain[0]), Math.log10(this.domain[1])];
    const t = (Math.log10(Math.max(value, 1e-10)) - logDomain[0]) / (logDomain[1] - logDomain[0]);
    return this.range[0] + t * (this.range[1] - this.range[0]);
  }

  invert(value: number): number {
    const logDomain = [Math.log10(this.domain[0]), Math.log10(this.domain[1])];
    const t = (value - this.range[0]) / (this.range[1] - this.range[0]);
    return Math.pow(10, logDomain[0] + t * (logDomain[1] - logDomain[0]));
  }
}

// ---- Data Point Types ----

export interface DataPoint {
  x: number;
  y: number;
  label?: string;
  color?: string;
  size?: number;
}

export interface SeriesData {
  name: string;
  points: DataPoint[];
  color: string;
  lineWidth: number;
  fillOpacity: number;
}

// ---- Chart Configuration ----

export interface ChartConfig {
  width: number;
  height: number;
  padding: { top: number; right: number; bottom: number; left: number };
  backgroundColor: string;
  gridColor: string;
  axisColor: string;
  fontFamily: string;
  fontSize: number;
  fontColor: string;
  showGrid: boolean;
  showAxes: boolean;
  showLabels: boolean;
  animationDuration: number;
}

const DEFAULT_CHART_CONFIG: ChartConfig = {
  width: 800,
  height: 400,
  padding: { top: 20, right: 20, bottom: 40, left: 60 },
  backgroundColor: '#0d1117',
  gridColor: '#21262d',
  axisColor: '#8b949e',
  fontFamily: 'Inter, system-ui, sans-serif',
  fontSize: 12,
  fontColor: '#c9d1d9',
  showGrid: true,
  showAxes: true,
  showLabels: true,
  animationDuration: 300,
};

// ---- Computed Layout ----

interface ChartLayout {
  plotX: number;      // Left edge of plot area
  plotY: number;      // Top edge of plot area
  plotWidth: number;  // Width of plot area
  plotHeight: number; // Height of plot area
  xScale: LinearScale;
  yScale: LinearScale;
}

// ---- Chart Types ----

export type ChartType = 'line' | 'bar' | 'scatter' | 'area';

// ---- Tick Generator ----

function generateTicks(min: number, max: number, count: number): number[] {
  const range = max - min;
  const rawStep = range / count;
  // Snap to "nice" numbers: 1, 2, 5, 10, 20, 50...
  const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const residual = rawStep / magnitude;
  let niceStep: number;
  if (residual <= 1.5) niceStep = magnitude;
  else if (residual <= 3.5) niceStep = 2 * magnitude;
  else if (residual <= 7.5) niceStep = 5 * magnitude;
  else niceStep = 10 * magnitude;

  const ticks: number[] = [];
  let tick = Math.ceil(min / niceStep) * niceStep;
  while (tick <= max) {
    ticks.push(Math.round(tick * 1e10) / 1e10); // fix float precision
    tick += niceStep;
  }
  return ticks;
}

// ---- Core Engine ----

export class OmniChartRendererEngine {
  private config: ChartConfig;
  private series: SeriesData[] = [];

  constructor(config: Partial<ChartConfig> = {}) {
    this.config = { ...DEFAULT_CHART_CONFIG, ...config };
  }

  // ---------- Data Management ----------

  addSeries(data: SeriesData): void {
    this.series.push(data);
  }

  clearSeries(): void {
    this.series = [];
  }

  // ---------- Layout Computation ----------

  private computeLayout(): ChartLayout {
    const { width, height, padding } = this.config;

    const plotX = padding.left;
    const plotY = padding.top;
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;

    // Compute data bounds across all series
    let xMin = Infinity, xMax = -Infinity;
    let yMin = Infinity, yMax = -Infinity;

    for (const s of this.series) {
      for (const p of s.points) {
        if (p.x < xMin) xMin = p.x;
        if (p.x > xMax) xMax = p.x;
        if (p.y < yMin) yMin = p.y;
        if (p.y > yMax) yMax = p.y;
      }
    }

    // Fallback for empty data
    if (!isFinite(xMin)) { xMin = 0; xMax = 1; }
    if (!isFinite(yMin)) { yMin = 0; yMax = 1; }

    // Add 5% padding to data range
    const xPad = (xMax - xMin) * 0.05 || 0.5;
    const yPad = (yMax - yMin) * 0.05 || 0.5;

    const xScale = new LinearScale([xMin - xPad, xMax + xPad], [plotX, plotX + plotWidth]);
    // Y axis is inverted in canvas (top = 0)
    const yScale = new LinearScale([yMin - yPad, yMax + yPad], [plotY + plotHeight, plotY]);

    return { plotX, plotY, plotWidth, plotHeight, xScale, yScale };
  }

  // ---------- Canvas Rendering ----------

  render(ctx: CanvasRenderingContext2D, chartType: ChartType = 'line'): void {
    const { width, height, backgroundColor } = this.config;

    // Background
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, width, height);

    if (this.series.length === 0) return;

    const layout = this.computeLayout();

    // Grid & Axes
    if (this.config.showGrid) this.renderGrid(ctx, layout);
    if (this.config.showAxes) this.renderAxes(ctx, layout);

    // Data
    for (const s of this.series) {
      switch (chartType) {
        case 'line':
          this.renderLine(ctx, s, layout);
          break;
        case 'bar':
          this.renderBars(ctx, s, layout);
          break;
        case 'scatter':
          this.renderScatter(ctx, s, layout);
          break;
        case 'area':
          this.renderArea(ctx, s, layout);
          break;
      }
    }
  }

  private renderGrid(ctx: CanvasRenderingContext2D, layout: ChartLayout): void {
    const { gridColor, fontSize, fontColor, fontFamily } = this.config;
    const { plotX, plotY, plotWidth, plotHeight, xScale, yScale } = layout;

    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 0.5;
    ctx.font = `${fontSize}px ${fontFamily}`;
    ctx.fillStyle = fontColor;

    // Y grid lines + labels
    const yTicks = generateTicks(yScale.domain[0], yScale.domain[1], 6);
    for (const tick of yTicks) {
      const y = yScale.map(tick);
      ctx.beginPath();
      ctx.moveTo(plotX, y);
      ctx.lineTo(plotX + plotWidth, y);
      ctx.stroke();

      if (this.config.showLabels) {
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.formatNumber(tick), plotX - 8, y);
      }
    }

    // X grid lines + labels
    const xTicks = generateTicks(xScale.domain[0], xScale.domain[1], 8);
    for (const tick of xTicks) {
      const x = xScale.map(tick);
      ctx.beginPath();
      ctx.moveTo(x, plotY);
      ctx.lineTo(x, plotY + plotHeight);
      ctx.stroke();

      if (this.config.showLabels) {
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText(this.formatNumber(tick), x, plotY + plotHeight + 8);
      }
    }
  }

  private renderAxes(ctx: CanvasRenderingContext2D, layout: ChartLayout): void {
    const { plotX, plotY, plotWidth, plotHeight } = layout;
    ctx.strokeStyle = this.config.axisColor;
    ctx.lineWidth = 1;

    // Y axis
    ctx.beginPath();
    ctx.moveTo(plotX, plotY);
    ctx.lineTo(plotX, plotY + plotHeight);
    ctx.stroke();

    // X axis
    ctx.beginPath();
    ctx.moveTo(plotX, plotY + plotHeight);
    ctx.lineTo(plotX + plotWidth, plotY + plotHeight);
    ctx.stroke();
  }

  private renderLine(ctx: CanvasRenderingContext2D, series: SeriesData, layout: ChartLayout): void {
    if (series.points.length < 2) return;

    const { xScale, yScale } = layout;

    ctx.strokeStyle = series.color;
    ctx.lineWidth = series.lineWidth;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();

    const sorted = [...series.points].sort((a, b) => a.x - b.x);
    ctx.moveTo(xScale.map(sorted[0].x), yScale.map(sorted[0].y));

    for (let i = 1; i < sorted.length; i++) {
      ctx.lineTo(xScale.map(sorted[i].x), yScale.map(sorted[i].y));
    }
    ctx.stroke();
  }

  private renderBars(ctx: CanvasRenderingContext2D, series: SeriesData, layout: ChartLayout): void {
    const { xScale, yScale, plotHeight, plotY } = layout;
    const barWidth = Math.max(2, layout.plotWidth / series.points.length * 0.7);
    const baseline = plotY + plotHeight;

    ctx.fillStyle = series.color;

    for (const p of series.points) {
      const x = xScale.map(p.x) - barWidth / 2;
      const y = yScale.map(p.y);
      const h = baseline - y;
      ctx.fillRect(x, y, barWidth, h);
    }
  }

  private renderScatter(ctx: CanvasRenderingContext2D, series: SeriesData, layout: ChartLayout): void {
    const { xScale, yScale } = layout;

    for (const p of series.points) {
      const cx = xScale.map(p.x);
      const cy = yScale.map(p.y);
      const radius = p.size ?? 4;

      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color ?? series.color;
      ctx.fill();
    }
  }

  private renderArea(ctx: CanvasRenderingContext2D, series: SeriesData, layout: ChartLayout): void {
    if (series.points.length < 2) return;
    const { xScale, yScale, plotHeight, plotY } = layout;
    const sorted = [...series.points].sort((a, b) => a.x - b.x);
    const baseline = plotY + plotHeight;

    // Filled area
    ctx.beginPath();
    ctx.moveTo(xScale.map(sorted[0].x), baseline);
    for (const p of sorted) {
      ctx.lineTo(xScale.map(p.x), yScale.map(p.y));
    }
    ctx.lineTo(xScale.map(sorted[sorted.length - 1].x), baseline);
    ctx.closePath();
    ctx.fillStyle = series.color;
    ctx.globalAlpha = series.fillOpacity;
    ctx.fill();
    ctx.globalAlpha = 1.0;

    // Outline
    this.renderLine(ctx, series, layout);
  }

  // ---------- Utilities ----------

  private formatNumber(n: number): string {
    if (Math.abs(n) >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
    if (Math.abs(n) >= 1_000) return (n / 1_000).toFixed(1) + 'K';
    if (Number.isInteger(n)) return n.toString();
    return n.toFixed(2);
  }

  // ---------- SVG Export ----------

  toSVG(chartType: ChartType = 'line'): string {
    if (this.series.length === 0) return '<svg></svg>';

    const { width, height, backgroundColor } = this.config;
    const layout = this.computeLayout();
    const parts: string[] = [];

    parts.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">`);
    parts.push(`<rect width="${width}" height="${height}" fill="${backgroundColor}"/>`);

    // Render data as SVG paths
    for (const s of this.series) {
      const sorted = [...s.points].sort((a, b) => a.x - b.x);
      if (sorted.length < 2) continue;

      const pathParts = sorted.map((p, i) => {
        const x = layout.xScale.map(p.x).toFixed(2);
        const y = layout.yScale.map(p.y).toFixed(2);
        return `${i === 0 ? 'M' : 'L'}${x},${y}`;
      });

      parts.push(`<path d="${pathParts.join(' ')}" stroke="${s.color}" stroke-width="${s.lineWidth}" fill="none"/>`);
    }

    parts.push('</svg>');
    return parts.join('\n');
  }

  // ---------- Diagnostics ----------

  diagnostics(): Record<string, unknown> {
    return {
      engine: 'OmniChartRendererEngine',
      layer: 'TypeScript UI',
      series_count: this.series.length,
      total_points: this.series.reduce((sum, s) => sum + s.points.length, 0),
      config: {
        width: this.config.width,
        height: this.config.height,
        show_grid: this.config.showGrid,
      },
      supported_types: ['line', 'bar', 'scatter', 'area'],
      export_formats: ['canvas', 'svg'],
      learned_logic: [
        'd3-linear-log-scale-system',
        'nice-tick-generation-algorithm',
        'functional-pipeline-data-to-shape',
        'canvas-and-svg-dual-rendering',
        'generic-scale-interface',
        'auto-domain-padding',
      ],
    };
  }
}
