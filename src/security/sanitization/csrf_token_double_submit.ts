// OMNI MOTHER SYSTEM - SECURITY LAYER
// CSRF Token Double Submit Validator.
// Enforces cross-site request forgery protection by correlating secure HttpOnly cookies with payload headers.

export type CsrfResult = 
    | { valid: true; error: null }
    | { valid: false; error: string };

export class CsrfDoubleSubmitValidator {
    
    /**
     * @brief Generates a cryptographically random token string.
     * To be generated on initial session creation and placed in BOTH an HttpOnly cookie 
     * AND a readable meta tag or custom response header for the SPA to read.
     */
    public static generateToken(): string {
        // Utilizing native Web Crypto API or Node crypto
        // Assuming environment supports crypto.getRandomValues
        const array = new Uint8Array(32);
        if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
            crypto.getRandomValues(array);
        } else {
            // Node.js fallback (if running in backend)
            // require('crypto').randomFillSync(array);
            throw new Error("OMNI_FATAL: Cryptographic RNG not available in this environment.");
        }
        
        return Buffer.from(array).toString('base64url');
    }

    /**
     * @brief Validates a state-changing HTTP Request against CSRF attacks.
     * 
     * @param cookieToken The token extracted directly from the secure HttpOnly cookie.
     * @param headerToken The token sent by the Javascript client in a custom header (e.g., X-CSRF-Token).
     */
    public static validateRequest(cookieToken: string | undefined, headerToken: string | undefined): CsrfResult {
        if (!cookieToken) {
            return { valid: false, error: "OMNI_FATAL: CSRF Cookie missing. Request denied." };
        }

        if (!headerToken) {
            return { valid: false, error: "OMNI_FATAL: CSRF Header missing. Request denied." };
        }

        // Constant-time string comparison to prevent timing attacks
        if (!this.constantTimeCompare(cookieToken, headerToken)) {
            return { valid: false, error: "OMNI_FATAL: CSRF Token mismatch. Possible cross-site request forgery detected." };
        }

        return { valid: true, error: null };
    }

    /**
     * @brief Compares two strings without early exit to prevent timing attacks on token checking.
     */
    private static constantTimeCompare(a: string, b: string): boolean {
        if (a.length !== b.length) {
            return false; // Length leaks timing, but for fixed-size CSRF tokens this is acceptable
        }

        let result = 0;
        for (let i = 0; i < a.length; i++) {
            // Bitwise XOR: 0 if identical, >0 if different.
            result |= (a.charCodeAt(i) ^ b.charCodeAt(i));
        }

        return result === 0;
    }
}
