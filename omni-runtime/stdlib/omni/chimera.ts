export async function __omni_inline_exec(lang: string, code: string, vars?: Record<string, any>): Promise<any> {
    const omni = (globalThis as any).OmniNative;
    if (!omni) {
        throw new Error("OMNI Kernel not found. Chimera Syntax requires OMNI Runtime.");
    }
    
    // We send variables as JSON string avoiding slow serialization for primitives where possible,
    // but JSON.stringify is fine for Batch 1.
    const res = omni.syscall("omni_inline_exec", {
        lang: lang,
        code: code,
        vars: JSON.stringify(vars || {})
    });
    
    if (res.error) throw new Error(res.error);
    
    // Attempt to parse JSON output if possible (e.g. stats dict from python)
    if (typeof res.result === 'string') {
        try {
            return JSON.parse(res.result);
        } catch(e) {
            return res.result; // Return raw string if not JSON
        }
    }
    return res.result;
}

// Inject automatically to global scope so Transpiler generated code can find it
(globalThis as any).__omni_inline_exec = __omni_inline_exec;
