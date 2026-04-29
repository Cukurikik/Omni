// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Express Middleware Chain (OMNI Zero-Mock Implementation)
// Implements mathematical sequential callback queue execution.

export type Result<T> = 
  | { value: T; isOk: true; error: null }
  | { value: null; isOk: false; error: string };

type RequestContext = { path: string; modifiedBy: string[] };

type Middleware = (req: RequestContext, next: (err?: string) => void) => void;

export class ExpressRouter {
    private stack: Middleware[] = [];

    public use(mw: Middleware) {
        this.stack.push(mw);
    }

    public handle(req: RequestContext): Result<RequestContext> {
        let index = 0;
        let finalError: string | null = null;
        let done = false;

        const next = (err?: string) => {
             if (err) {
                 finalError = err;
                 done = true;
                 return;
             }
             
             if (index >= this.stack.length) {
                 done = true;
                 return;
             }
             
             const mw = this.stack[index++];
             try {
                 mw(req, next);
             } catch (e: any) {
                 finalError = e.message || "Middleware exception";
                 done = true;
             }
        };

        next(); // Kicks off recursion depth mathematically

        if (finalError) {
             return { value: null, isOk: false, error: finalError };
        }

        return { value: req, isOk: true, error: null };
    }
}
