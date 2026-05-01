// OMNI MOTHER SYSTEM - SECURITY LAYER
// OAuth2 Proof Key for Code Exchange (PKCE) Validator

import { createHash } from 'crypto';

export type OmniResult<T, E> = 
  | { success: true; value: T; error: null }
  | { success: false; value: null; error: E };

export class PkceValidator {
    
    /**
     * Validates that the base64url encoded SHA-256 hash of the code_verifier
     * exactly matches the provided code_challenge.
     */
    public validateCodeChallenge(codeVerifier: string, codeChallenge: string, method: 'S256' | 'plain' = 'S256'): OmniResult<boolean, string> {
        if (!codeVerifier || codeVerifier.length < 43 || codeVerifier.length > 128) {
            return { success: false, value: null, error: "code_verifier must be between 43 and 128 characters" };
        }

        if (!codeChallenge || codeChallenge.length === 0) {
            return { success: false, value: null, error: "code_challenge cannot be empty" };
        }

        if (method === 'plain') {
            // Deprecated by RFC 7636, but handled for structural completeness. OMNI should reject.
            return { success: false, value: null, error: "'plain' method is explicitly forbidden by Omni Security Policy. Use S256." };
        }

        if (method === 'S256') {
            try {
                const computedChallenge = this.generateS256Challenge(codeVerifier);
                
                // Constant-time comparison to prevent timing attacks
                if (this.constantTimeCompare(computedChallenge, codeChallenge)) {
                    return { success: true, value: true, error: null };
                } else {
                    return { success: false, value: null, error: "code_challenge mismatch" };
                }
            } catch (e: any) {
                return { success: false, value: null, error: `Hashing failed: ${e.message}` };
            }
        }

        return { success: false, value: null, error: "Unsupported transformation method" };
    }

    private generateS256Challenge(verifier: string): string {
        const hash = createHash('sha256').update(verifier).digest();
        return this.base64UrlEncode(hash);
    }

    private base64UrlEncode(buffer: Buffer): string {
        return buffer.toString('base64')
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=/g, '');
    }

    private constantTimeCompare(a: string, b: string): boolean {
        if (a.length !== b.length) {
            return false;
        }
        let result = 0;
        for (let i = 0; i < a.length; i++) {
            result |= a.charCodeAt(i) ^ b.charCodeAt(i);
        }
        return result === 0;
    }
}
