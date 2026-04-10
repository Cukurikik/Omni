// ==========================================
// 🔗 OMNI-LAND: NATIVE URL PARSING
// ==========================================
// Go net/url stdlib — parser URL tercepat.
//
// IMPORT: import { url } from 'omni/url';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

export interface ParsedURL {
    protocol: string;
    hostname: string;
    port: string;
    pathname: string;
    search: string;
    hash: string;
    origin: string;
    host: string;
    href: string;
    query: Record<string, string>;
    username: string;
    password: string;
}

/**
 * Parse URL menjadi komponen terstruktur.
 * ⚡ Go net/url.Parse() — lebih strict dari WHATWG URL API.
 */
export function parse(rawUrl: string): ParsedURL {
    const res = OmniNative.syscall("url_parse", { url: rawUrl });
    if (res.error) throw new Error(`[OMNI-URL] ${res.error}`);
    return res.result as ParsedURL;
}

/**
 * Build URL dari komponen.
 */
export function format(components: Partial<ParsedURL>): string {
    const res = OmniNative.syscall("url_format", { components });
    return res.result as string;
}

/**
 * Resolve relative URL terhadap base URL.
 */
export function resolve(base: string, relative: string): string {
    const res = OmniNative.syscall("url_resolve", { base, relative });
    return res.result as string;
}

/**
 * Encode query string dari object.
 * Contoh: { foo: "bar", baz: "123" } → "foo=bar&baz=123"
 */
export function encodeQuery(params: Record<string, string>): string {
    const res = OmniNative.syscall("url_encode_query", { params });
    return res.result as string;
}

/**
 * Decode query string ke object.
 */
export function decodeQuery(queryString: string): Record<string, string> {
    const res = OmniNative.syscall("url_decode_query", { query: queryString });
    return res.result as Record<string, string>;
}

/**
 * URL-encode string (percent encoding).
 */
export function encode(str: string): string {
    const res = OmniNative.syscall("url_encode", { str });
    return res.result as string;
}

/**
 * URL-decode string.
 */
export function decode(str: string): string {
    const res = OmniNative.syscall("url_decode", { str });
    return res.result as string;
}

export const url = {
    parse,
    format,
    resolve,
    encodeQuery,
    decodeQuery,
    encode,
    decode,
};

export default url;
