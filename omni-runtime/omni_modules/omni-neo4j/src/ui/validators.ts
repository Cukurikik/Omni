// omni-neo4j â€” Client-Side Validators

export type ValidationResult = { valid: boolean; errors: string[] };

export const Validators = {
  required: (v: unknown): ValidationResult => ({ valid: v !== null && v !== undefined && v !== '', errors: v ? [] : ['Field is required'] }),
  minLength: (min: number) => (v: string): ValidationResult => ({ valid: v.length >= min, errors: v.length >= min ? [] : ['Min length ' + min] }),
  maxLength: (max: number) => (v: string): ValidationResult => ({ valid: v.length <= max, errors: v.length <= max ? [] : ['Max length ' + max] }),
  email: (v: string): ValidationResult => ({ valid: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), errors: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) ? [] : ['Invalid email'] }),
  url: (v: string): ValidationResult => { try { new URL(v); return { valid: true, errors: [] }; } catch { return { valid: false, errors: ['Invalid URL'] }; } },
  numeric: (v: string): ValidationResult => ({ valid: !isNaN(Number(v)), errors: !isNaN(Number(v)) ? [] : ['Must be numeric'] }),
  range: (min: number, max: number) => (v: number): ValidationResult => ({ valid: v >= min && v <= max, errors: v >= min && v <= max ? [] : ['Out of range'] }),
  compose: (...validators: ((v: any) => ValidationResult)[]) => (v: any): ValidationResult => {
    const errors: string[] = []; validators.forEach(fn => { const r = fn(v); errors.push(...r.errors); });
    return { valid: errors.length === 0, errors };
  },
};