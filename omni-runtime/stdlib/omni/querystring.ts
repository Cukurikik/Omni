// ==========================================
// 🧬 OMNI-LAND: NATIVE QUERYSTRING MODULE
// ==========================================
// Go net/url.Values untuk parsing/encoding query strings.
//
// IMPORT: import { querystring } from 'omni/querystring';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Parse query string ke object.
 * Contoh: "foo=bar&baz=123" → { foo: "bar", baz: "123" }
 */
export function parse(qs: string): Record<string, string | string[]> {
    const res = OmniNative.syscall("qs_parse", { query: qs });
    if (res.error) throw new Error(`[OMNI-QS] ${res.error}`);
    return res.result as Record<string, string | string[]>;
}

/**
 * Stringify object ke query string.
 * Contoh: { foo: "bar" } → "foo=bar"
 */
export function stringify(obj: Record<string, string | number | boolean | string[]>, sep?: string, eq?: string): string {
    const res = OmniNative.syscall("qs_stringify", { obj, sep: sep ?? "&", eq: eq ?? "=" });
    return res.result as string;
}

/**
 * Escape string untuk query parameter.
 */
export function escape(str: string): string {
    const res = OmniNative.syscall("qs_escape", { str });
    return res.result as string;
}

/**
 * Unescape escaped query parameter.
 */
export function unescape(str: string): string {
    const res = OmniNative.syscall("qs_unescape", { str });
    return res.result as string;
}

export const querystring = { parse, stringify, escape, unescape };
export default querystring;
