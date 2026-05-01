/**
 * OMNI Engine — OAuth2 Token Validator
 * Layer: Security
 * Implements: Validation logic for Bearer tokens
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

export class OAuth2Validator {
    /**
     * Validate the Authorization header structure
     */
    static validateHeader(authHeader: string): OmniResult<string> {
        if (!authHeader) {
            return fail("Authorization header is missing");
        }

        const parts = authHeader.split(' ');
        if (parts.length !== 2 || parts[0] !== 'Bearer') {
            return fail("Invalid Authorization header format. Expected 'Bearer <token>'");
        }

        const token = parts[1];
        if (token.length < 32) {
            return fail("Token length is suspiciously short");
        }

        return ok(token);
    }

    /**
     * Parse basic JWT payload without signature verification (for routing/metadata extraction)
     */
    static decodePayloadUnsafe(token: string): OmniResult<any> {
        const parts = token.split('.');
        if (parts.length !== 3) {
            return fail("Invalid JWT format");
        }

        try {
            // Buffer in Node or atob in Browser. Using a simple base64 decoder for Omni
            const base64Url = parts[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = Buffer.from(base64, 'base64').toString('utf8');
            return ok(JSON.parse(jsonPayload));
        } catch (e: any) {
            return fail(`Failed to decode JWT payload: ${e.message}`);
        }
    }
}
