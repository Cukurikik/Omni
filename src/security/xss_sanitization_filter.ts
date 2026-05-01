/**
 * OMNI Engine — XSS Sanitization Filter
 * Layer: Security
 * Implements: Context-aware HTML entity encoding
 */

export interface OmniResult<T> {
    value?: T;
    error?: string;
    is_ok: boolean;
}

export function ok<T>(value: T): OmniResult<T> {
    return { value, is_ok: true };
}

export function fail<T>(error: string): OmniResult<T> {
    return { error, is_ok: false };
}

export class XSSFilter {
    private static readonly HTML_ENTITIES: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
    };

    /**
     * Escape characters that are dangerous in HTML context
     */
    static escapeHtml(input: string): OmniResult<string> {
        if (input === null || input === undefined) {
            return ok('');
        }
        
        if (typeof input !== 'string') {
            return fail("Input must be a string");
        }

        const escaped = input.replace(/[&<>"'/`=]/g, (char) => {
            return XSSFilter.HTML_ENTITIES[char] || char;
        });

        return ok(escaped);
    }

    /**
     * Validate URL protocol to prevent javascript: and vbscript: attacks
     */
    static validateUrlProtocol(url: string): OmniResult<string> {
        if (!url) return fail("Empty URL");

        const parsed = url.toLowerCase().trim();
        if (parsed.startsWith('javascript:') || parsed.startsWith('vbscript:') || parsed.startsWith('data:')) {
            return fail("Dangerous URL protocol rejected");
        }

        return ok(url);
    }
}
