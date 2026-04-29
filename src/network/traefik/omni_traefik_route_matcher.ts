// OMNI Traefik Route Matcher Engine — Network Layer (TypeScript)
// Absorbing traefik/traefik dynamic routing logic
// Host and PathPrefix exact match rule topology 

export type TraefikResult<T> = {
    ok: boolean;
    value: T | null;
    error: string;
};

export interface RouteRule {
    targetService: string;
    hostRule: string | null;
    pathPrefixRule: string | null;
    priority: number;
}

export class OmniTraefikRouteMatcher {
    private evaluations: number = 0;
    private routers: RouteRule[] = [];

    public add_router(rule: RouteRule): TraefikResult<boolean> {
        try {
            if (!rule.targetService) {
                return { ok: false, value: false, error: "Missing target service structural bounds." };
            }
            this.routers.push(rule);
            
            // Sort by priority (highest first), length of path prefix (fallback)
            this.routers.sort((a, b) => {
                if (a.priority !== b.priority) return b.priority - a.priority;
                let aLen = a.pathPrefixRule ? a.pathPrefixRule.length : 0;
                let bLen = b.pathPrefixRule ? b.pathPrefixRule.length : 0;
                return bLen - aLen; 
            });
            
            return { ok: true, value: true, error: "" };
        } catch (e: any) {
             return { ok: false, value: false, error: `Router Panic: ${e.message}` };
        }
    }

    public execute_request_routing(host: string, path: string): TraefikResult<string> {
        try {
            if (!host || !path) {
                return { ok: false, value: null, error: "Empty request bounds." };
            }

            this.evaluations++;

            for (const rule of this.routers) {
                let hostMatch = true;
                let pathMatch = true;

                if (rule.hostRule) {
                    if (rule.hostRule !== host) hostMatch = false;
                }

                if (rule.pathPrefixRule) {
                    if (!path.startsWith(rule.pathPrefixRule)) pathMatch = false;
                }

                if (hostMatch && pathMatch) {
                    return { ok: true, value: rule.targetService, error: "" };
                }
            }

            return { ok: true, value: "502_BAD_GATEWAY", error: "" };
            
        } catch (e: any) {
             return { ok: false, value: null, error: `Evaluation Panic: ${e.message}` };
        }
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: "OmniTraefikRouteMatcher",
            rules_registered: this.routers.length,
            routes_evaluated: this.evaluations,
            status: "Operational"
        };
    }
}
