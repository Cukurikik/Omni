// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Drizzle Buffer Sim (OMNI Zero-Mock Implementation)
// Implements MySQL logical query buffer pool simulator.

export type Result<T> = 
  | { value: T; isOk: true; error: null }
  | { value: null; isOk: false; error: string };

type BufferPage = {
  pageId: string;
  dirty: boolean;
  pinCount: number;
};

// Implements a strict LRU buffer pool replacer policy similar to MySQL ORM layers
export class BufferPoolManager {
  private capacity: number;
  private pages: Map<string, BufferPage>;
  private lruList: string[]; // Front is most recently used

  constructor(capacity: number) {
      this.capacity = capacity;
      this.pages = new Map();
      this.lruList = [];
  }

  // Brings a page into memory
  public fetchPage(pageId: string): Result<BufferPage> {
      if (this.pages.has(pageId)) {
          // Update LRU
          this.lruList = this.lruList.filter(id => id !== pageId);
          this.lruList.unshift(pageId);
          const p = this.pages.get(pageId)!;
          p.pinCount++;
          return { value: p, isOk: true, error: null };
      }

      // Need to load page
      if (this.pages.size >= this.capacity) {
          // Eviction
          let victimId: string | null = null;
          // Start from end of LRU (least recently used)
          for (let i = this.lruList.length - 1; i >= 0; i--) {
              const pid = this.lruList[i];
              if (this.pages.get(pid)?.pinCount === 0) {
                  victimId = pid;
                  break;
              }
          }

          if (victimId === null) {
              return { value: null, isOk: false, error: "Buffer pool OOM: all pages pinned." };
          }

          if (this.pages.get(victimId)!.dirty) {
             // In real DB, flush to disk here.
          }

          this.pages.delete(victimId);
          this.lruList = this.lruList.filter(id => id !== victimId);
      }

      // Insert new page
      const newPage: BufferPage = { pageId, dirty: false, pinCount: 1 };
      this.pages.set(pageId, newPage);
      this.lruList.unshift(pageId);

      return { value: newPage, isOk: true, error: null };
  }

  public unpinPage(pageId: string, isDirty: boolean): Result<boolean> {
      if (!this.pages.has(pageId)) {
           return { value: null, isOk: false, error: "Page not in buffer pool." };
      }
      
      const p = this.pages.get(pageId)!;
      if (p.pinCount <= 0) {
           return { value: null, isOk: false, error: "Page already fully unpinned." };
      }
      
      p.pinCount--;
      if (isDirty) p.dirty = true;
      
      return { value: true, isOk: true, error: null };
  }
}
