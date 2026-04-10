// ==========================================
// 🧪 OMNI-LAND: NATIVE ASSERT MODULE
// ==========================================
// Lightweight assertion library untuk testing.
//
// IMPORT: import { assert } from 'omni/assert';
// ==========================================

export class AssertionError extends Error {
    actual: any;
    expected: any;
    operator: string;

    constructor(message: string, actual: any, expected: any, operator: string) {
        super(message);
        this.name = "AssertionError";
        this.actual = actual;
        this.expected = expected;
        this.operator = operator;
    }
}

/**
 * Assert bahwa value adalah truthy.
 */
export function ok(value: any, message?: string): void {
    if (!value) {
        throw new AssertionError(
            message || `Expected truthy but got ${JSON.stringify(value)}`,
            value, true, "ok"
        );
    }
}

/**
 * Assert deep equality (JSON.stringify comparison).
 */
export function deepEqual(actual: any, expected: any, message?: string): void {
    const a = JSON.stringify(actual);
    const b = JSON.stringify(expected);
    if (a !== b) {
        throw new AssertionError(
            message || `Expected ${b} but got ${a}`,
            actual, expected, "deepEqual"
        );
    }
}

/**
 * Assert strict equality (===).
 */
export function strictEqual(actual: any, expected: any, message?: string): void {
    if (actual !== expected) {
        throw new AssertionError(
            message || `Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`,
            actual, expected, "strictEqual"
        );
    }
}

/**
 * Assert not equal (!==).
 */
export function notEqual(actual: any, expected: any, message?: string): void {
    if (actual === expected) {
        throw new AssertionError(
            message || `Expected not ${JSON.stringify(expected)}`,
            actual, expected, "notEqual"
        );
    }
}

/**
 * Assert bahwa fungsi melempar error.
 */
export function throws(fn: () => void, message?: string): void {
    let threw = false;
    try { fn(); } catch { threw = true; }
    if (!threw) {
        throw new AssertionError(
            message || "Expected function to throw",
            "no throw", "throw", "throws"
        );
    }
}

/**
 * Assert bahwa fungsi TIDAK melempar error.
 */
export function doesNotThrow(fn: () => void, message?: string): void {
    try {
        fn();
    } catch (e: any) {
        throw new AssertionError(
            message || `Expected function not to throw but got: ${e.message}`,
            e.message, "no throw", "doesNotThrow"
        );
    }
}

/**
 * Force fail assertion.
 */
export function fail(message?: string): never {
    throw new AssertionError(
        message || "Assertion failed",
        undefined, undefined, "fail"
    );
}

/**
 * Assert string matches regex.
 */
export function match(actual: string, regex: RegExp, message?: string): void {
    if (!regex.test(actual)) {
        throw new AssertionError(
            message || `Expected "${actual}" to match ${regex}`,
            actual, regex.toString(), "match"
        );
    }
}

export const assert = {
    ok,
    deepEqual,
    strictEqual,
    notEqual,
    throws,
    doesNotThrow,
    fail,
    match,
};

export default assert;
