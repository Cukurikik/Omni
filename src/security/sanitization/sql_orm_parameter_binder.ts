// OMNI MOTHER SYSTEM - SECURITY LAYER
// SQL ORM Parameter Binder.
// Strictly enforces parameterized database querying, annihilating SQL Injection vectors.

export type SqlValue = string | number | boolean | null | Date;

export class SqlInjectionError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "SqlInjectionError";
    }
}

export class ParameterizedQuery {
    public readonly sql: string;
    public readonly parameters: any[];

    constructor(sql: string, parameters: any[]) {
        this.sql = sql;
        this.parameters = parameters;
    }
}

/**
 * @brief Tagged Template Literal function for securely composing SQL.
 * 
 * Usage:
 * const email = "user@domain.com";
 * const query = sql`SELECT * FROM users WHERE email = ${email}`;
 * 
 * Bypassing this by manually concatenating strings into `sql` will fail compilation or trigger errors.
 */
export function sql(strings: TemplateStringsArray, ...values: SqlValue[]): ParameterizedQuery {
    // 1. Structural Validation
    if (!Array.isArray(strings) || !strings.raw) {
        throw new SqlInjectionError("OMNI_FATAL: Queries must be constructed using Tagged Template Literals.");
    }

    // 2. Build the parameter-safe string (e.g. Postgres $1, $2 or MySQL ?, ?)
    let queryString = "";
    const queryParams: any[] = [];

    for (let i = 0; i < strings.length; i++) {
        queryString += strings[i];
        
        if (i < values.length) {
            // Omni standardizes on Postgres $index style for this boundary representation
            queryString += `$${i + 1}`;
            
            // Value is passed COMPLETELY separately to the driver.
            // It never enters the SQL AST parser as a command.
            queryParams.push(values[i]);
        }
    }

    return new ParameterizedQuery(queryString.trim(), queryParams);
}
