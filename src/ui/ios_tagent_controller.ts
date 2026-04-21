// ===========================================================================
// OMNI UI LAYER — iOS TAGENT WEBDRIVERAGENT CONTROLLER
// ===========================================================================
// Source Paradigm : nicklockwood/iVersion / appium/WebDriverAgent / iOS-Tagent
// Domain Layer   : UI (Static typing, contract-first API)
// Language        : TypeScript
// Function        : Communicates with WebDriverAgent (WDA) on iOS devices via
//                   HTTP to perform UI automation: element queries, gestures,
//                   screenshot capture, app lifecycle, and session management
// ===========================================================================

interface WDASessionInfo {
    sessionId: string;
    bundleId: string;
    deviceUDID: string;
    status: 'active' | 'inactive' | 'error';
    createdAt: number;
}

interface WDAElement {
    id: string;
    type: string;      // XCUIElementType (e.g. "Button", "TextField")
    label: string;
    value: string | null;
    isEnabled: boolean;
    isVisible: boolean;
    frame: { x: number; y: number; width: number; height: number };
}

interface GestureConfig {
    type: 'tap' | 'doubleTap' | 'longPress' | 'swipe' | 'pinch';
    x: number;
    y: number;
    duration?: number;    // ms (for longPress)
    toX?: number;         // destination (for swipe)
    toY?: number;
    velocity?: number;    // for swipe speed
    scale?: number;       // for pinch
}

interface AppInfo {
    bundleId: string;
    name: string;
    pid: number;
    state: 'running' | 'suspended' | 'not_running';
}

// ---- Command Builder (mirrors WDA HTTP API) --------------------------------

class WDACommand {
    private baseUrl: string;

    constructor(wdaHost: string, wdaPort: number = 8100) {
        this.baseUrl = `http://${wdaHost}:${wdaPort}`;
    }

    /** POST /session — create a new WDA session. */
    createSession(bundleId: string): { method: string; url: string; body: object } {
        return {
            method: 'POST',
            url: `${this.baseUrl}/session`,
            body: {
                desiredCapabilities: {
                    bundleId,
                    shouldWaitForQuiescence: false,
                }
            }
        };
    }

    /** DELETE /session/:id — destroy a session. */
    deleteSession(sessionId: string) {
        return { method: 'DELETE', url: `${this.baseUrl}/session/${sessionId}`, body: {} };
    }

    /** POST /session/:id/element — find element by predicate. */
    findElement(sessionId: string, using: string, value: string) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/session/${sessionId}/element`,
            body: { using, value }
        };
    }

    /** POST /session/:id/elements — find multiple elements. */
    findElements(sessionId: string, using: string, value: string) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/session/${sessionId}/elements`,
            body: { using, value }
        };
    }

    /** POST /session/:id/element/:eid/click — tap an element. */
    clickElement(sessionId: string, elementId: string) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/session/${sessionId}/element/${elementId}/click`,
            body: {}
        };
    }

    /** POST /session/:id/element/:eid/value — type into element. */
    typeText(sessionId: string, elementId: string, text: string) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/session/${sessionId}/element/${elementId}/value`,
            body: { value: text.split('') }
        };
    }

    /** GET /screenshot — capture screen as base64 PNG. */
    screenshot() {
        return { method: 'GET', url: `${this.baseUrl}/screenshot`, body: {} };
    }

    /** POST /session/:id/wda/touch/perform — custom gesture. */
    performGesture(sessionId: string, gesture: GestureConfig) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/session/${sessionId}/wda/touch/perform`,
            body: { actions: [this.buildGestureAction(gesture)] }
        };
    }

    /** GET /session/:id/source — get full page source (XML). */
    getPageSource(sessionId: string) {
        return { method: 'GET', url: `${this.baseUrl}/session/${sessionId}/source`, body: {} };
    }

    /** POST /wda/apps/launch — launch app by bundleId. */
    launchApp(bundleId: string) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/wda/apps/launch`,
            body: { bundleId }
        };
    }

    /** POST /wda/apps/terminate — terminate app. */
    terminateApp(bundleId: string) {
        return {
            method: 'POST',
            url: `${this.baseUrl}/wda/apps/terminate`,
            body: { bundleId }
        };
    }

    /** POST /wda/pressButton — press hardware button. */
    pressButton(button: 'home' | 'volumeUp' | 'volumeDown') {
        return {
            method: 'POST',
            url: `${this.baseUrl}/wda/pressButton`,
            body: { name: button }
        };
    }

    /** GET /status — WDA health check. */
    healthCheck() {
        return { method: 'GET', url: `${this.baseUrl}/status`, body: {} };
    }

    private buildGestureAction(g: GestureConfig): object {
        switch (g.type) {
            case 'tap':
                return { action: 'tap', options: { x: g.x, y: g.y } };
            case 'doubleTap':
                return { action: 'tap', options: { x: g.x, y: g.y, count: 2 } };
            case 'longPress':
                return { action: 'press', options: { x: g.x, y: g.y, duration: g.duration || 1000 } };
            case 'swipe':
                return {
                    action: 'swipe',
                    options: { fromX: g.x, fromY: g.y, toX: g.toX, toY: g.toY, velocity: g.velocity || 500 }
                };
            case 'pinch':
                return { action: 'pinch', options: { x: g.x, y: g.y, scale: g.scale || 0.5 } };
        }
    }
}

// ---- Session Manager -------------------------------------------------------

class iOSTagentController {
    private cmd: WDACommand;
    private sessions: Map<string, WDASessionInfo> = new Map();

    constructor(wdaHost: string, wdaPort: number = 8100) {
        this.cmd = new WDACommand(wdaHost, wdaPort);
        console.log(`[TAGENT-OMNI-TS] Controller initialized: ${wdaHost}:${wdaPort}`);
    }

    async createSession(bundleId: string): Promise<WDASessionInfo> {
        console.log(`[TAGENT-OMNI-TS] Creating session for: ${bundleId}`);
        const req = this.cmd.createSession(bundleId);
        // Production: fetch(req.url, { method: req.method, body: JSON.stringify(req.body) })
        const session: WDASessionInfo = {
            sessionId: `session-${Date.now()}`,
            bundleId,
            deviceUDID: 'SIMULATED',
            status: 'active',
            createdAt: Date.now(),
        };
        this.sessions.set(session.sessionId, session);
        console.log(`[TAGENT-OMNI-TS] Session created: ${session.sessionId}`);
        return session;
    }

    getSession(sessionId: string): WDASessionInfo | undefined {
        return this.sessions.get(sessionId);
    }

    getActiveSessions(): WDASessionInfo[] {
        return Array.from(this.sessions.values()).filter(s => s.status === 'active');
    }
}

export { iOSTagentController, WDACommand, WDAElement, GestureConfig, AppInfo };
