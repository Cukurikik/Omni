/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI FORM VALIDATOR ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : zod + yup + valibot schema validation concepts
// Logic Inherited: TypeScript / UI Layer (Composable Type-Safe Validation)
// Domain Layer   : UI (TypeScript Core)
// ===========================================================================
//
// By studying Zod's chainable API and Valibot's tree-shakeable design,
// Mother learned that modern form validation is best expressed as a
// composable chain of pure validator functions. Each validator returns
// a Result<T, ValidationError[]> — the same monadic pattern used
// throughout the OMNI Framework, replacing try/catch entirely.

// ---- Result Type (Monadic Error Handling) ----

export type ValidationResult<T> =
  | { ok: true; value: T }
  | { ok: false; errors: ValidationError[] };

export interface ValidationError {
  path: string;
  rule: string;
  message: string;
  received: unknown;
  expected?: string;
}

// ---- Validator Type ----

export type Validator<T> = (value: unknown, path: string) => ValidationResult<T>;

// ---- Primitive Validators (Chainable) ----

export function string(): StringValidator {
  return new StringValidator();
}

export function number(): NumberValidator {
  return new NumberValidator();
}

export function boolean(): BooleanValidator {
  return new BooleanValidator();
}

export function array<T>(itemValidator: { validate: Validator<T> }): ArrayValidator<T> {
  return new ArrayValidator(itemValidator);
}

export function object<T extends Record<string, { validate: Validator<unknown> }>>(
  shape: T
): ObjectValidator<T> {
  return new ObjectValidator(shape);
}

// ---- String Validator ----

export class StringValidator {
  private rules: Array<(val: string, path: string) => ValidationError | null> = [];

  validate: Validator<string> = (value: unknown, path: string) => {
    if (typeof value !== 'string') {
      return {
        ok: false,
        errors: [{ path, rule: 'type', message: 'Expected string', received: value, expected: 'string' }],
      };
    }

    const errors: ValidationError[] = [];
    for (const rule of this.rules) {
      const err = rule(value, path);
      if (err) errors.push(err);
    }

    return errors.length > 0 ? { ok: false, errors } : { ok: true, value };
  };

  min(length: number): this {
    this.rules.push((val, path) =>
      val.length < length
        ? { path, rule: 'min', message: `Minimum length is ${length}`, received: val.length, expected: `>= ${length}` }
        : null
    );
    return this;
  }

  max(length: number): this {
    this.rules.push((val, path) =>
      val.length > length
        ? { path, rule: 'max', message: `Maximum length is ${length}`, received: val.length, expected: `<= ${length}` }
        : null
    );
    return this;
  }

  email(): this {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    this.rules.push((val, path) =>
      !emailRegex.test(val)
        ? { path, rule: 'email', message: 'Invalid email format', received: val, expected: 'valid email' }
        : null
    );
    return this;
  }

  url(): this {
    this.rules.push((val, path) => {
      try {
        new URL(val);
        return null;
      } catch {
        return { path, rule: 'url', message: 'Invalid URL format', received: val, expected: 'valid URL' };
      }
    });
    return this;
  }

  regex(pattern: RegExp, message?: string): this {
    this.rules.push((val, path) =>
      !pattern.test(val)
        ? { path, rule: 'regex', message: message ?? `Does not match pattern ${pattern}`, received: val }
        : null
    );
    return this;
  }

  nonempty(): this {
    this.rules.push((val, path) =>
      val.trim().length === 0
        ? { path, rule: 'nonempty', message: 'Cannot be empty', received: val }
        : null
    );
    return this;
  }

  uuid(): this {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    this.rules.push((val, path) =>
      !uuidRegex.test(val)
        ? { path, rule: 'uuid', message: 'Invalid UUID format', received: val }
        : null
    );
    return this;
  }
}

// ---- Number Validator ----

export class NumberValidator {
  private rules: Array<(val: number, path: string) => ValidationError | null> = [];

  validate: Validator<number> = (value: unknown, path: string) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return {
        ok: false,
        errors: [{ path, rule: 'type', message: 'Expected number', received: value, expected: 'number' }],
      };
    }

    const errors: ValidationError[] = [];
    for (const rule of this.rules) {
      const err = rule(value, path);
      if (err) errors.push(err);
    }

    return errors.length > 0 ? { ok: false, errors } : { ok: true, value };
  };

  min(n: number): this {
    this.rules.push((val, path) =>
      val < n
        ? { path, rule: 'min', message: `Must be at least ${n}`, received: val, expected: `>= ${n}` }
        : null
    );
    return this;
  }

  max(n: number): this {
    this.rules.push((val, path) =>
      val > n
        ? { path, rule: 'max', message: `Must be at most ${n}`, received: val, expected: `<= ${n}` }
        : null
    );
    return this;
  }

  integer(): this {
    this.rules.push((val, path) =>
      !Number.isInteger(val)
        ? { path, rule: 'integer', message: 'Must be an integer', received: val }
        : null
    );
    return this;
  }

  positive(): this {
    this.rules.push((val, path) =>
      val <= 0
        ? { path, rule: 'positive', message: 'Must be positive', received: val }
        : null
    );
    return this;
  }

  between(min: number, max: number): this {
    this.rules.push((val, path) =>
      val < min || val > max
        ? { path, rule: 'between', message: `Must be between ${min} and ${max}`, received: val }
        : null
    );
    return this;
  }
}

// ---- Boolean Validator ----

export class BooleanValidator {
  validate: Validator<boolean> = (value: unknown, path: string) => {
    if (typeof value !== 'boolean') {
      return {
        ok: false,
        errors: [{ path, rule: 'type', message: 'Expected boolean', received: value, expected: 'boolean' }],
      };
    }
    return { ok: true, value };
  };
}

// ---- Array Validator ----

export class ArrayValidator<T> {
  private itemValidator: { validate: Validator<T> };
  private minLen?: number;
  private maxLen?: number;

  constructor(itemValidator: { validate: Validator<T> }) {
    this.itemValidator = itemValidator;
  }

  validate: Validator<T[]> = (value: unknown, path: string) => {
    if (!Array.isArray(value)) {
      return {
        ok: false,
        errors: [{ path, rule: 'type', message: 'Expected array', received: value, expected: 'array' }],
      };
    }

    const errors: ValidationError[] = [];

    if (this.minLen !== undefined && value.length < this.minLen) {
      errors.push({ path, rule: 'minLength', message: `Array must have at least ${this.minLen} items`, received: value.length });
    }
    if (this.maxLen !== undefined && value.length > this.maxLen) {
      errors.push({ path, rule: 'maxLength', message: `Array must have at most ${this.maxLen} items`, received: value.length });
    }

    // Validate each item
    const items: T[] = [];
    for (let i = 0; i < value.length; i++) {
      const result = this.itemValidator.validate(value[i], `${path}[${i}]`);
      if (result.ok) {
        items.push(result.value);
      } else {
        errors.push(...result.errors);
      }
    }

    return errors.length > 0 ? { ok: false, errors } : { ok: true, value: items };
  };

  min(length: number): this {
    this.minLen = length;
    return this;
  }

  max(length: number): this {
    this.maxLen = length;
    return this;
  }
}

// ---- Object Validator ----

type InferShape<T extends Record<string, { validate: Validator<unknown> }>> = {
  [K in keyof T]: T[K] extends { validate: Validator<infer U> } ? U : never;
};

export class ObjectValidator<T extends Record<string, { validate: Validator<unknown> }>> {
  private shape: T;
  private strict: boolean = false;

  constructor(shape: T) {
    this.shape = shape;
  }

  validate: Validator<InferShape<T>> = (value: unknown, path: string = '') => {
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
      return {
        ok: false,
        errors: [{ path, rule: 'type', message: 'Expected object', received: value, expected: 'object' }],
      };
    }

    const obj = value as Record<string, unknown>;
    const errors: ValidationError[] = [];
    const validated: Record<string, unknown> = {};

    // Validate each field in schema
    for (const [key, validator] of Object.entries(this.shape)) {
      const fieldPath = path ? `${path}.${key}` : key;
      const fieldValue = obj[key];

      if (fieldValue === undefined) {
        errors.push({
          path: fieldPath,
          rule: 'required',
          message: `Field "${key}" is required`,
          received: undefined,
        });
        continue;
      }

      const result = validator.validate(fieldValue, fieldPath);
      if (result.ok) {
        validated[key] = result.value;
      } else {
        errors.push(...result.errors);
      }
    }

    // Strict mode: reject unknown fields
    if (this.strict) {
      for (const key of Object.keys(obj)) {
        if (!(key in this.shape)) {
          const fieldPath = path ? `${path}.${key}` : key;
          errors.push({
            path: fieldPath,
            rule: 'unknown',
            message: `Unknown field "${key}"`,
            received: obj[key],
          });
        }
      }
    }

    return errors.length > 0
      ? { ok: false, errors }
      : { ok: true, value: validated as InferShape<T> };
  };

  strictMode(): this {
    this.strict = true;
    return this;
  }
}

// ---- Form State Manager ----

export interface FieldState {
  value: unknown;
  touched: boolean;
  dirty: boolean;
  errors: ValidationError[];
}

export class OmniFormValidatorEngine {
  private fields: Map<string, FieldState> = new Map();
  private schema: ObjectValidator<Record<string, { validate: Validator<unknown> }>> | null = null;
  private validationCount: number = 0;
  private lastValidationMs: number = 0;

  setSchema(schema: ObjectValidator<Record<string, { validate: Validator<unknown> }>>): void {
    this.schema = schema;
  }

  setField(name: string, value: unknown): void {
    const existing = this.fields.get(name);
    this.fields.set(name, {
      value,
      touched: existing?.touched ?? false,
      dirty: true,
      errors: existing?.errors ?? [],
    });
  }

  touchField(name: string): void {
    const field = this.fields.get(name);
    if (field) {
      field.touched = true;
    }
  }

  getField(name: string): FieldState | undefined {
    return this.fields.get(name);
  }

  getValues(): Record<string, unknown> {
    const values: Record<string, unknown> = {};
    for (const [key, field] of this.fields) {
      values[key] = field.value;
    }
    return values;
  }

  validateAll(): ValidationResult<Record<string, unknown>> {
    if (!this.schema) {
      return { ok: true, value: this.getValues() };
    }

    const start = Date.now();
    const result = this.schema.validate(this.getValues(), '');
    this.lastValidationMs = Date.now() - start;
    this.validationCount++;

    // Update field errors
    for (const [, field] of this.fields) {
      field.errors = [];
    }

    if (!result.ok) {
      for (const err of result.errors) {
        const fieldName = err.path.split('.')[0];
        const field = this.fields.get(fieldName);
        if (field) {
          field.errors.push(err);
        }
      }
    }

    return result;
  }

  isValid(): boolean {
    const result = this.validateAll();
    return result.ok;
  }

  getErrors(): ValidationError[] {
    const errors: ValidationError[] = [];
    for (const [, field] of this.fields) {
      errors.push(...field.errors);
    }
    return errors;
  }

  reset(): void {
    this.fields.clear();
  }

  diagnostics(): Record<string, unknown> {
    return {
      engine: 'OmniFormValidatorEngine',
      layer: 'TypeScript UI',
      field_count: this.fields.size,
      dirty_fields: Array.from(this.fields.values()).filter(f => f.dirty).length,
      touched_fields: Array.from(this.fields.values()).filter(f => f.touched).length,
      error_count: this.getErrors().length,
      validation_count: this.validationCount,
      last_validation_ms: this.lastValidationMs,
      has_schema: this.schema !== null,
      learned_logic: [
        'zod-chainable-validator-api',
        'monadic-result-type-pattern',
        'composable-pure-validator-functions',
        'recursive-object-schema-validation',
        'type-inference-from-schema-shape',
        'strict-mode-unknown-field-rejection',
      ],
    };
  }
}
