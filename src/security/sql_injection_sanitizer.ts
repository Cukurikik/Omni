/**
 * OMNI Engine — SQL Injection Sanitizer
 * Layer: Security
 * Implements: Validation and escaping logic for Raw SQL queries
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

export class SqlSanitizer {
    /**
     * Detects malicious SQL patterns
     */
    static detectSqlInjection(input: string): OmniResult<boolean> {
        if (!input) return ok(false);

        const sqlRegex = /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|UNION|EXEC|EXECUTE)\b)|([';]+)|(--)/i;
        
        if (sqlRegex.test(input)) {
            return ok(true); // Injection detected
        }

        return ok(false); // Clean
    }

    /**
     * Escapes single quotes for standard SQL text fields
     */
    static escapeString(input: string): OmniResult<string> {
        if (input === null || input === undefined) {
            return ok('');
        }
        
        if (typeof input !== 'string') {
            return fail("Input must be a string");
        }

        // Replace single quote with two single quotes (standard SQL escape)
        const escaped = input.replace(/'/g, "''");
        return ok(escaped);
    }
}
