/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI VIRTUAL LIST ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
// ===========================================================================
// Absorbed From  : react-virtualized + tanstack/virtual + vue-virtual-scroller
// Logic Inherited: TypeScript / UI Layer (Windowed Virtual Scrolling)
// Domain Layer   : UI (TypeScript Core)
// ===========================================================================
//
// By studying react-virtualized and @tanstack/virtual, Mother learned
// that rendering 100K+ list items requires windowed virtualization:
//   1. Only render items visible in the viewport + overscan buffer
//   2. Use absolute positioning (CSS transform) for each rendered item
//   3. Total scroll height is computed from item sizes (fixed or variable)
//   4. On scroll, recalculate which items are visible (binary search)
//
// This engine is framework-agnostic: it computes layout metadata,
// and the framework (React/Vue/Svelte) handles actual DOM rendering.

// ---- Types ----

export interface VirtualItem {
  index: number;
  start: number;   // Offset from top of scroll container (px)
  end: number;     // Start + size
  size: number;
  key: string | number;
}

export type ItemSizeGetter = (index: number) => number;

export interface VirtualListConfig {
  /** Total number of items in the list. */
  count: number;
  /** Height of the scroll viewport (px). */
  viewportHeight: number;
  /** Fixed item height, or a function for variable heights. */
  itemSize: number | ItemSizeGetter;
  /** Number of extra items to render outside the viewport (top & bottom). */
  overscan: number;
  /** Generate a unique key for each item (defaults to index). */
  getItemKey?: (index: number) => string | number;
  /** Gap between items (px). */
  gap: number;
}

const DEFAULT_CONFIG: Partial<VirtualListConfig> = {
  overscan: 5,
  gap: 0,
};

// ---- Precomputed Size Table (for variable heights) ----

class SizeTable {
  private offsets: number[];    // offsets[i] = cumulative offset of item i
  private sizes: number[];
  private totalSize: number;

  constructor(count: number, sizeGetter: ItemSizeGetter, gap: number) {
    this.offsets = new Array(count);
    this.sizes = new Array(count);
    let offset = 0;

    for (let i = 0; i < count; i++) {
      const size = sizeGetter(i);
      this.offsets[i] = offset;
      this.sizes[i] = size;
      offset += size + (i < count - 1 ? gap : 0);
    }

    this.totalSize = offset;
  }

  getOffset(index: number): number {
    return this.offsets[index] ?? 0;
  }

  getSize(index: number): number {
    return this.sizes[index] ?? 0;
  }

  getTotalSize(): number {
    return this.totalSize;
  }

  /**
   * Binary search: find the first item whose offset >= scrollTop.
   */
  findStartIndex(scrollTop: number): number {
    let lo = 0;
    let hi = this.offsets.length - 1;

    while (lo <= hi) {
      const mid = (lo + hi) >>> 1;
      if (this.offsets[mid] < scrollTop) {
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }

    return Math.max(0, lo - 1);
  }

  /**
   * Find the last item whose offset + size <= scrollTop + viewportHeight.
   */
  findEndIndex(scrollTop: number, viewportHeight: number): number {
    const bottom = scrollTop + viewportHeight;
    let lo = 0;
    let hi = this.offsets.length - 1;

    while (lo <= hi) {
      const mid = (lo + hi) >>> 1;
      if (this.offsets[mid] <= bottom) {
        lo = mid + 1;
      } else {
        hi = mid - 1;
      }
    }

    return Math.min(this.offsets.length - 1, lo);
  }
}

// ---- Core Engine ----

export class OmniVirtualListEngine {
  private config: VirtualListConfig;
  private sizeTable: SizeTable | null = null;
  private fixedItemSize: number | null = null;
  private scrollTop: number = 0;
  private lastComputedItems: VirtualItem[] = [];
  private totalComputations: number = 0;

  constructor(config: Partial<VirtualListConfig> & { count: number; viewportHeight: number; itemSize: number | ItemSizeGetter }) {
    this.config = { ...DEFAULT_CONFIG, ...config } as VirtualListConfig;
    this.buildSizeTable();
  }

  // ---- Configuration ----

  /**
   * Update configuration (e.g., item count changed, viewport resized).
   */
  updateConfig(partial: Partial<VirtualListConfig>): void {
    this.config = { ...this.config, ...partial };
    this.buildSizeTable();
  }

  private buildSizeTable(): void {
    const { count, itemSize, gap } = this.config;

    if (typeof itemSize === 'number') {
      this.fixedItemSize = itemSize;
      this.sizeTable = null;
    } else {
      this.fixedItemSize = null;
      this.sizeTable = new SizeTable(count, itemSize, gap);
    }
  }

  // ---- Scroll ----

  /**
   * Update the scroll position. Call this on every scroll event.
   * Returns the new set of visible virtual items.
   */
  setScrollTop(scrollTop: number): VirtualItem[] {
    this.scrollTop = Math.max(0, scrollTop);
    return this.computeVisibleItems();
  }

  /**
   * Scroll to a specific item index.
   * Returns the scroll offset to apply.
   */
  scrollToIndex(index: number): number {
    const clamped = Math.max(0, Math.min(index, this.config.count - 1));
    const offset = this.getItemOffset(clamped);
    this.scrollTop = offset;
    return offset;
  }

  // ---- Layout Computation ----

  /**
   * Compute which items should be rendered given the current scroll position.
   * This is the hot path — called on every scroll event.
   */
  computeVisibleItems(): VirtualItem[] {
    this.totalComputations++;

    const { count, viewportHeight, overscan, gap } = this.config;
    if (count === 0) {
      this.lastComputedItems = [];
      return [];
    }

    let startIndex: number;
    let endIndex: number;

    if (this.fixedItemSize !== null) {
      // Fixed height: O(1) computation
      const effectiveItemSize = this.fixedItemSize + gap;
      startIndex = Math.floor(this.scrollTop / effectiveItemSize);
      endIndex = Math.ceil((this.scrollTop + viewportHeight) / effectiveItemSize);
    } else if (this.sizeTable) {
      // Variable height: O(log N) binary search
      startIndex = this.sizeTable.findStartIndex(this.scrollTop);
      endIndex = this.sizeTable.findEndIndex(this.scrollTop, viewportHeight);
    } else {
      this.lastComputedItems = [];
      return [];
    }

    // Apply overscan
    startIndex = Math.max(0, startIndex - overscan);
    endIndex = Math.min(count - 1, endIndex + overscan);

    // Build virtual items
    const items: VirtualItem[] = [];
    const getKey = this.config.getItemKey ?? ((i: number) => i);

    for (let i = startIndex; i <= endIndex; i++) {
      const offset = this.getItemOffset(i);
      const size = this.getItemSize(i);
      items.push({
        index: i,
        start: offset,
        end: offset + size,
        size,
        key: getKey(i),
      });
    }

    this.lastComputedItems = items;
    return items;
  }

  // ---- Size & Offset Helpers ----

  private getItemOffset(index: number): number {
    if (this.fixedItemSize !== null) {
      return index * (this.fixedItemSize + this.config.gap);
    }
    return this.sizeTable?.getOffset(index) ?? 0;
  }

  private getItemSize(index: number): number {
    if (this.fixedItemSize !== null) {
      return this.fixedItemSize;
    }
    return this.sizeTable?.getSize(index) ?? 0;
  }

  // ---- Public Getters ----

  /**
   * Total scrollable height (px).
   * Use this as the height of the inner scroll container.
   */
  getTotalSize(): number {
    const { count, gap } = this.config;
    if (this.fixedItemSize !== null) {
      return count * (this.fixedItemSize + gap) - (count > 0 ? gap : 0);
    }
    return this.sizeTable?.getTotalSize() ?? 0;
  }

  /**
   * Get the last computed visible items (no recomputation).
   */
  getVisibleItems(): VirtualItem[] {
    return this.lastComputedItems;
  }

  /**
   * Number of items currently rendered (including overscan).
   */
  getRenderedCount(): number {
    return this.lastComputedItems.length;
  }

  /**
   * Range of currently visible item indices.
   */
  getVisibleRange(): { start: number; end: number } {
    if (this.lastComputedItems.length === 0) return { start: 0, end: 0 };
    return {
      start: this.lastComputedItems[0].index,
      end: this.lastComputedItems[this.lastComputedItems.length - 1].index,
    };
  }

  // ---- Diagnostics ----

  diagnostics(): Record<string, unknown> {
    return {
      engine: 'OmniVirtualListEngine',
      layer: 'TypeScript UI',
      total_items: this.config.count,
      viewport_height: this.config.viewportHeight,
      overscan: this.config.overscan,
      gap: this.config.gap,
      is_fixed_size: this.fixedItemSize !== null,
      item_size: this.fixedItemSize ?? 'variable',
      total_scroll_height: this.getTotalSize(),
      current_scroll_top: this.scrollTop,
      rendered_count: this.getRenderedCount(),
      visible_range: this.getVisibleRange(),
      total_computations: this.totalComputations,
      render_ratio: this.config.count > 0
        ? `${this.getRenderedCount()}/${this.config.count} (${((this.getRenderedCount() / this.config.count) * 100).toFixed(2)}%)`
        : '0/0',
      learned_logic: [
        'windowed-virtualization-overscan',
        'binary-search-variable-height',
        'o1-fixed-height-computation',
        'absolute-positioning-css-transform',
        'framework-agnostic-layout-engine',
        'precomputed-offset-table',
        'scroll-to-index-navigation',
      ],
    };
  }
}
