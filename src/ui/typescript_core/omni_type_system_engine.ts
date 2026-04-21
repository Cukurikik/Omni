/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI TYPE SYSTEM ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : Zod + io-ts + typebox + ts-pattern + Effect Schema
// Logic Inherited: TypeScript / Interface Layer (Runtime Type Validation)
// ===========================================================================
//
// By studying Zod and io-ts, Mother learned TypeScript type patterns:
//   1. Schema = runtime validator + static type extractor
//   2. .parse() throws, .safeParse() returns Result<T, Error>
//   3. Composition: .and(), .or(), .transform(), .refine()
//   4. Recursive schemas enable tree/graph validation
//   5. Branded types add nominal typing to structural TypeScript

// ============================================================
// PART 1: Result Type
// ============================================================

type Result<T, E = string> =
  | { success: true; data: T }
  | { success: false; error: E; issues: ValidationIssue[] };

interface ValidationIssue {
  path: (string | number)[];
  message: string;
  code: string;
}

function success<T>(data: T): Result<T> {
  return { success: true, data };
}

function failure(error: string, issues: ValidationIssue[] = []): Result<never> {
  return { success: false, error, issues };
}

// ============================================================
// PART 2: Schema Base Class
// ============================================================

abstract class Schema<T> {
  abstract _parse(input: unknown, path: (string | number)[]): Result<T>;

  /** Parse and throw on failure. */
  parse(input: unknown): T {
    const result = this._parse(input, []);
    if (!result.success) {
      throw new Error(`Validation failed: ${result.error}\n${
        result.issues.map(i => `  - ${i.path.join('.')}: ${i.message}`).join('\n')
      }`);
    }
    return result.data;
  }

  /** Parse without throwing. */
  safeParse(input: unknown): Result<T> {
    return this._parse(input, []);
  }

  /** Transform the parsed value. */
  transform<U>(fn: (value: T) => U): TransformSchema<T, U> {
    return new TransformSchema(this, fn);
  }

  /** Add custom refinement. */
  refine(check: (value: T) => boolean, message: string = "Refinement failed"): RefinementSchema<T> {
    return new RefinementSchema(this, check, message);
  }

  /** Make optional (T | undefined). */
  optional(): OptionalSchema<T> {
    return new OptionalSchema(this);
  }

  /** Make nullable (T | null). */
  nullable(): NullableSchema<T> {
    return new NullableSchema(this);
  }

  /** Set default value. */
  default(defaultValue: T): DefaultSchema<T> {
    return new DefaultSchema(this, defaultValue);
  }

  /** Union with another schema. */
  or<U>(other: Schema<U>): UnionSchema<T | U> {
    return new UnionSchema([this as Schema<any>, other as Schema<any>]);
  }

  /** Intersection with another schema. */
  and<U>(other: Schema<U>): IntersectionSchema<T & U> {
    return new IntersectionSchema(this as Schema<any>, other as Schema<any>);
  }
}

// ============================================================
// PART 3: Primitive Schemas
// ============================================================

class StringSchema extends Schema<string> {
  private _minLength?: number;
  private _maxLength?: number;
  private _pattern?: RegExp;
  private _email?: boolean;
  private _url?: boolean;

  _parse(input: unknown, path: (string | number)[]): Result<string> {
    if (typeof input !== 'string') {
      return failure("Expected string", [{ path, message: `Expected string, got ${typeof input}`, code: "invalid_type" }]);
    }
    if (this._minLength !== undefined && input.length < this._minLength) {
      return failure("String too short", [{ path, message: `Min length ${this._minLength}, got ${input.length}`, code: "too_small" }]);
    }
    if (this._maxLength !== undefined && input.length > this._maxLength) {
      return failure("String too long", [{ path, message: `Max length ${this._maxLength}, got ${input.length}`, code: "too_big" }]);
    }
    if (this._pattern && !this._pattern.test(input)) {
      return failure("Pattern mismatch", [{ path, message: `Does not match pattern ${this._pattern}`, code: "invalid_pattern" }]);
    }
    if (this._email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input)) {
      return failure("Invalid email", [{ path, message: "Invalid email format", code: "invalid_email" }]);
    }
    if (this._url) {
      try { new URL(input); } catch {
        return failure("Invalid URL", [{ path, message: "Invalid URL format", code: "invalid_url" }]);
      }
    }
    return success(input);
  }

  min(n: number): this { this._minLength = n; return this; }
  max(n: number): this { this._maxLength = n; return this; }
  pattern(re: RegExp): this { this._pattern = re; return this; }
  email(): this { this._email = true; return this; }
  url(): this { this._url = true; return this; }
}

class NumberSchema extends Schema<number> {
  private _min?: number;
  private _max?: number;
  private _int?: boolean;
  private _positive?: boolean;
  private _finite?: boolean;

  _parse(input: unknown, path: (string | number)[]): Result<number> {
    if (typeof input !== 'number' || Number.isNaN(input)) {
      return failure("Expected number", [{ path, message: `Expected number, got ${typeof input}`, code: "invalid_type" }]);
    }
    if (this._finite && !Number.isFinite(input)) {
      return failure("Must be finite", [{ path, message: "Must be finite", code: "not_finite" }]);
    }
    if (this._int && !Number.isInteger(input)) {
      return failure("Must be integer", [{ path, message: "Must be integer", code: "not_integer" }]);
    }
    if (this._positive && input <= 0) {
      return failure("Must be positive", [{ path, message: "Must be positive", code: "not_positive" }]);
    }
    if (this._min !== undefined && input < this._min) {
      return failure(`Min ${this._min}`, [{ path, message: `Must be >= ${this._min}`, code: "too_small" }]);
    }
    if (this._max !== undefined && input > this._max) {
      return failure(`Max ${this._max}`, [{ path, message: `Must be <= ${this._max}`, code: "too_big" }]);
    }
    return success(input);
  }

  min(n: number): this { this._min = n; return this; }
  max(n: number): this { this._max = n; return this; }
  int(): this { this._int = true; return this; }
  positive(): this { this._positive = true; return this; }
  finite(): this { this._finite = true; return this; }
}

class BooleanSchema extends Schema<boolean> {
  _parse(input: unknown, path: (string | number)[]): Result<boolean> {
    if (typeof input !== 'boolean') {
      return failure("Expected boolean", [{ path, message: `Expected boolean, got ${typeof input}`, code: "invalid_type" }]);
    }
    return success(input);
  }
}

class LiteralSchema<T extends string | number | boolean> extends Schema<T> {
  constructor(private _literal: T) { super(); }
  _parse(input: unknown, path: (string | number)[]): Result<T> {
    if (input !== this._literal) {
      return failure(`Expected ${this._literal}`, [{ path, message: `Expected literal ${this._literal}`, code: "invalid_literal" }]);
    }
    return success(this._literal);
  }
}

// ============================================================
// PART 4: Composite Schemas
// ============================================================

class ObjectSchema<T extends Record<string, any>> extends Schema<T> {
  private _strict: boolean = false;

  constructor(private _shape: { [K in keyof T]: Schema<T[K]> }) { super(); }

  _parse(input: unknown, path: (string | number)[]): Result<T> {
    if (typeof input !== 'object' || input === null || Array.isArray(input)) {
      return failure("Expected object", [{ path, message: "Expected object", code: "invalid_type" }]);
    }

    const obj = input as Record<string, unknown>;
    const result: Record<string, any> = {};
    const allIssues: ValidationIssue[] = [];

    for (const [key, schema] of Object.entries(this._shape)) {
      const fieldResult = (schema as Schema<any>)._parse(obj[key], [...path, key]);
      if (!fieldResult.success) {
        allIssues.push(...fieldResult.issues);
      } else {
        result[key] = fieldResult.data;
      }
    }

    if (this._strict) {
      for (const key of Object.keys(obj)) {
        if (!(key in this._shape)) {
          allIssues.push({ path: [...path, key], message: "Unexpected key", code: "unrecognized_key" });
        }
      }
    }

    if (allIssues.length > 0) {
      return failure("Object validation failed", allIssues);
    }

    return success(result as T);
  }

  strict(): this { this._strict = true; return this; }

  extend<U extends Record<string, any>>(extra: { [K in keyof U]: Schema<U[K]> }): ObjectSchema<T & U> {
    return new ObjectSchema({ ...this._shape, ...extra } as any);
  }

  pick<K extends keyof T>(...keys: K[]): ObjectSchema<Pick<T, K>> {
    const picked: any = {};
    for (const key of keys) {
      picked[key] = this._shape[key];
    }
    return new ObjectSchema(picked);
  }

  omit<K extends keyof T>(...keys: K[]): ObjectSchema<Omit<T, K>> {
    const omitted: any = { ...this._shape };
    for (const key of keys) {
      delete omitted[key];
    }
    return new ObjectSchema(omitted);
  }
}

class ArraySchema<T> extends Schema<T[]> {
  private _minLength?: number;
  private _maxLength?: number;
  private _unique?: boolean;

  constructor(private _element: Schema<T>) { super(); }

  _parse(input: unknown, path: (string | number)[]): Result<T[]> {
    if (!Array.isArray(input)) {
      return failure("Expected array", [{ path, message: "Expected array", code: "invalid_type" }]);
    }
    if (this._minLength !== undefined && input.length < this._minLength) {
      return failure("Array too short", [{ path, message: `Min length ${this._minLength}`, code: "too_small" }]);
    }
    if (this._maxLength !== undefined && input.length > this._maxLength) {
      return failure("Array too long", [{ path, message: `Max length ${this._maxLength}`, code: "too_big" }]);
    }

    const result: T[] = [];
    const allIssues: ValidationIssue[] = [];

    for (let i = 0; i < input.length; i++) {
      const elemResult = this._element._parse(input[i], [...path, i]);
      if (!elemResult.success) {
        allIssues.push(...elemResult.issues);
      } else {
        result.push(elemResult.data);
      }
    }

    if (allIssues.length > 0) {
      return failure("Array validation failed", allIssues);
    }

    return success(result);
  }

  min(n: number): this { this._minLength = n; return this; }
  max(n: number): this { this._maxLength = n; return this; }
  unique(): this { this._unique = true; return this; }
}

class UnionSchema<T> extends Schema<T> {
  constructor(private _schemas: Schema<any>[]) { super(); }

  _parse(input: unknown, path: (string | number)[]): Result<T> {
    for (const schema of this._schemas) {
      const result = schema._parse(input, path);
      if (result.success) return result;
    }
    return failure("No union member matched", [{ path, message: "No union member matched", code: "invalid_union" }]);
  }
}

class IntersectionSchema<T> extends Schema<T> {
  constructor(private _a: Schema<any>, private _b: Schema<any>) { super(); }

  _parse(input: unknown, path: (string | number)[]): Result<T> {
    const ra = this._a._parse(input, path);
    if (!ra.success) return ra;
    const rb = this._b._parse(input, path);
    if (!rb.success) return rb;
    return success({ ...ra.data, ...rb.data } as T);
  }
}

class TransformSchema<I, O> extends Schema<O> {
  constructor(private _inner: Schema<I>, private _fn: (value: I) => O) { super(); }

  _parse(input: unknown, path: (string | number)[]): Result<O> {
    const result = this._inner._parse(input, path);
    if (!result.success) return result as any;
    try {
      return success(this._fn(result.data));
    } catch (e: any) {
      return failure("Transform failed", [{ path, message: e.message, code: "transform_error" }]);
    }
  }
}

class RefinementSchema<T> extends Schema<T> {
  constructor(private _inner: Schema<T>, private _check: (v: T) => boolean, private _msg: string) { super(); }

  _parse(input: unknown, path: (string | number)[]): Result<T> {
    const result = this._inner._parse(input, path);
    if (!result.success) return result;
    if (!this._check(result.data)) {
      return failure(this._msg, [{ path, message: this._msg, code: "custom_refinement" }]);
    }
    return success(result.data);
  }
}

class OptionalSchema<T> extends Schema<T | undefined> {
  constructor(private _inner: Schema<T>) { super(); }
  _parse(input: unknown, path: (string | number)[]): Result<T | undefined> {
    if (input === undefined) return success(undefined);
    return this._inner._parse(input, path);
  }
}

class NullableSchema<T> extends Schema<T | null> {
  constructor(private _inner: Schema<T>) { super(); }
  _parse(input: unknown, path: (string | number)[]): Result<T | null> {
    if (input === null) return success(null);
    return this._inner._parse(input, path);
  }
}

class DefaultSchema<T> extends Schema<T> {
  constructor(private _inner: Schema<T>, private _default: T) { super(); }
  _parse(input: unknown, path: (string | number)[]): Result<T> {
    if (input === undefined || input === null) return success(this._default);
    return this._inner._parse(input, path);
  }
}

// ============================================================
// Factory Functions (Public API)
// ============================================================

const o = {
  string: () => new StringSchema(),
  number: () => new NumberSchema(),
  boolean: () => new BooleanSchema(),
  literal: <T extends string | number | boolean>(value: T) => new LiteralSchema(value),
  object: <T extends Record<string, any>>(shape: { [K in keyof T]: Schema<T[K]> }) => new ObjectSchema(shape),
  array: <T>(element: Schema<T>) => new ArraySchema(element),
  union: <T extends Schema<any>[]>(...schemas: T) => new UnionSchema(schemas),
};

// ============================================================
// Diagnostics
// ============================================================

function diagnostics() {
  return {
    engine: "OmniTypeSystemEngine",
    layer: "TypeScript Interface",
    schemas: [
      "StringSchema", "NumberSchema", "BooleanSchema", "LiteralSchema",
      "ObjectSchema", "ArraySchema", "UnionSchema", "IntersectionSchema",
      "TransformSchema", "RefinementSchema", "OptionalSchema", "NullableSchema",
    ],
    methods: ["parse", "safeParse", "transform", "refine", "optional", "nullable", "default", "or", "and"],
    learned_logic: [
      "zod-schema-parse-safeParse",
      "result-type-monadic-error",
      "path-tracking-nested-validation",
      "fluent-builder-chain-config",
      "object-extend-pick-omit",
      "union-first-match-wins",
      "intersection-merge-both",
      "transform-derive-output-type",
    ],
  };
}

export {
  Schema, StringSchema, NumberSchema, BooleanSchema, LiteralSchema,
  ObjectSchema, ArraySchema, UnionSchema, IntersectionSchema,
  TransformSchema, RefinementSchema, OptionalSchema, NullableSchema,
  DefaultSchema, o, diagnostics,
};
export type { Result, ValidationIssue };
