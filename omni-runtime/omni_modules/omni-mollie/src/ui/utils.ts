// omni-mollie â€” Utility Functions

export const sleep = (ms: number): Promise<void> => new Promise(r => setTimeout(r, ms));
export const retry = async <T>(fn: () => Promise<T>, attempts: number = 3, delay: number = 1000): Promise<T> => {
  for (let i = 0; i < attempts; i++) { try { return await fn(); } catch (e) { if (i === attempts - 1) throw e; await sleep(delay * (i + 1)); } }
  throw new Error('Retry exhausted');
};
export const debounce = <T extends (...args: any[]) => any>(fn: T, ms: number) => { let timer: any; return (...args: Parameters<T>) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); }; };
export const throttle = <T extends (...args: any[]) => any>(fn: T, ms: number) => { let last = 0; return (...args: Parameters<T>) => { const now = Date.now(); if (now - last >= ms) { last = now; fn(...args); } }; };
export const deepClone = <T>(obj: T): T => JSON.parse(JSON.stringify(obj));
export const uniqueId = (): string => Math.random().toString(36).substring(2) + Date.now().toString(36);
export const formatBytes = (bytes: number): string => { const units = ['B', 'KB', 'MB', 'GB', 'TB']; let i = 0; while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++; } return bytes.toFixed(2) + ' ' + units[i]; };