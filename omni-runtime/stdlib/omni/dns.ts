// ==========================================
// 🔍 OMNI-LAND: NATIVE DNS RESOLVER
// ==========================================
// Go net.LookupHost — resolver DNS native OS.
//
// IMPORT: import { dns } from 'omni/dns';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

/**
 * Resolve hostname ke IP addresses.
 */
export function lookup(hostname: string): string[] {
    const res = OmniNative.syscall("dns_lookup", { hostname });
    if (res.error) throw new Error(`[OMNI-DNS] ${res.error}`);
    return res.addresses as string[];
}

/**
 * Reverse DNS lookup — IP ke hostnames.
 */
export function reverse(ip: string): string[] {
    const res = OmniNative.syscall("dns_reverse", { ip });
    if (res.error) throw new Error(`[OMNI-DNS] ${res.error}`);
    return res.hostnames as string[];
}

/**
 * Resolve MX records.
 */
export function resolveMX(hostname: string): Array<{ host: string; priority: number }> {
    const res = OmniNative.syscall("dns_resolve_mx", { hostname });
    if (res.error) throw new Error(`[OMNI-DNS] ${res.error}`);
    return res.records as Array<{ host: string; priority: number }>;
}

/**
 * Resolve TXT records.
 */
export function resolveTXT(hostname: string): string[][] {
    const res = OmniNative.syscall("dns_resolve_txt", { hostname });
    if (res.error) throw new Error(`[OMNI-DNS] ${res.error}`);
    return res.records as string[][];
}

/**
 * Resolve NS records.
 */
export function resolveNS(hostname: string): string[] {
    const res = OmniNative.syscall("dns_resolve_ns", { hostname });
    if (res.error) throw new Error(`[OMNI-DNS] ${res.error}`);
    return res.records as string[];
}

/**
 * Resolve CNAME record.
 */
export function resolveCNAME(hostname: string): string {
    const res = OmniNative.syscall("dns_resolve_cname", { hostname });
    if (res.error) throw new Error(`[OMNI-DNS] ${res.error}`);
    return res.cname as string;
}

export const dns = {
    lookup,
    reverse,
    resolveMX,
    resolveTXT,
    resolveNS,
    resolveCNAME,
};

export default dns;
