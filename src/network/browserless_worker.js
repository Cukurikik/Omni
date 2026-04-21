// ===========================================================================
// OMNI NETWORK LAYER — BROWSERLESS HEADLESS CHROME WORKER
// ===========================================================================
// Source Paradigm : browserless/browserless
// Domain Layer   : Network (Event loop, non-blocking I/O, browser runtime)
// Language        : JavaScript (Node.js)
// Function        : Headless Chrome session pool manager with concurrency
//                   limits, page lifecycle, screenshot/PDF generation,
//                   JavaScript evaluation, and resource tracking
// ===========================================================================

'use strict';

// ---- Session Pool ---------------------------------------------------------

/**
 * @typedef {Object} BrowserSession
 * @property {string} id
 * @property {string} status      - "idle" | "active" | "closed"
 * @property {Date} createdAt
 * @property {Date} lastUsedAt
 * @property {number} pagesOpened
 * @property {number} memoryMB
 */

class SessionPool {
    constructor(maxConcurrent = 10, sessionTimeoutMs = 60000) {
        this.maxConcurrent = maxConcurrent;
        this.sessionTimeoutMs = sessionTimeoutMs;
        /** @type {Map<string, BrowserSession>} */
        this.sessions = new Map();
        this.totalCreated = 0;
        console.log(`[BROWSERLESS-OMNI-JS] Pool initialized (max: ${maxConcurrent})`);
    }

    /**
     * Acquire a browser session from the pool.
     * @returns {BrowserSession|null}
     */
    acquire() {
        // Reuse idle session if available
        for (const [id, session] of this.sessions) {
            if (session.status === 'idle') {
                session.status = 'active';
                session.lastUsedAt = new Date();
                console.log(`[BROWSERLESS-OMNI-JS] Reusing session: ${id}`);
                return session;
            }
        }

        // Create new if under limit
        if (this.sessions.size < this.maxConcurrent) {
            const session = this._createSession();
            console.log(`[BROWSERLESS-OMNI-JS] Created new session: ${session.id}`);
            return session;
        }

        console.log('[BROWSERLESS-OMNI-JS] Pool exhausted — request queued.');
        return null;
    }

    /**
     * Release a session back to idle.
     */
    release(sessionId) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.status = 'idle';
            session.lastUsedAt = new Date();
            console.log(`[BROWSERLESS-OMNI-JS] Released session: ${sessionId}`);
        }
    }

    /**
     * Close and remove a session.
     */
    destroy(sessionId) {
        const session = this.sessions.get(sessionId);
        if (session) {
            session.status = 'closed';
            this.sessions.delete(sessionId);
            console.log(`[BROWSERLESS-OMNI-JS] Destroyed session: ${sessionId}`);
        }
    }

    /**
     * Clean up sessions that have been idle for too long.
     */
    cleanup() {
        const now = Date.now();
        let cleaned = 0;
        for (const [id, session] of this.sessions) {
            if (session.status === 'idle' && (now - session.lastUsedAt.getTime()) > this.sessionTimeoutMs) {
                this.destroy(id);
                cleaned++;
            }
        }
        if (cleaned > 0) {
            console.log(`[BROWSERLESS-OMNI-JS] Cleaned ${cleaned} expired session(s).`);
        }
        return cleaned;
    }

    _createSession() {
        this.totalCreated++;
        const session = {
            id: `s-${this.totalCreated}-${Date.now().toString(36)}`,
            status: 'active',
            createdAt: new Date(),
            lastUsedAt: new Date(),
            pagesOpened: 0,
            memoryMB: 0,
        };
        this.sessions.set(session.id, session);
        return session;
    }

    getStats() {
        const active = Array.from(this.sessions.values()).filter(s => s.status === 'active').length;
        const idle = Array.from(this.sessions.values()).filter(s => s.status === 'idle').length;
        return { active, idle, total: this.sessions.size, totalCreated: this.totalCreated };
    }
}

// ---- Browserless Worker ---------------------------------------------------

/**
 * @typedef {Object} PageTask
 * @property {"screenshot"|"pdf"|"evaluate"|"scrape"|"navigate"} type
 * @property {string} url
 * @property {Object} options
 */

class BrowserlessWorker {
    constructor(options = {}) {
        this.pool = new SessionPool(options.maxSessions || 10, options.timeout || 60000);
        this.defaultViewport = {
            width: options.viewportWidth || 1920,
            height: options.viewportHeight || 1080,
        };
        this.blockAds = options.blockAds || false;
        this.requestLog = [];
        console.log('[BROWSERLESS-OMNI-JS] Worker ready.');
    }

    /**
     * Take a screenshot of a URL.
     * @returns {Promise<{data: string, format: string, width: number, height: number}>}
     */
    async screenshot(url, options = {}) {
        const session = this.pool.acquire();
        if (!session) throw new Error('No available sessions');

        console.log(`[BROWSERLESS-OMNI-JS] Screenshot: ${url}`);
        session.pagesOpened++;

        // Production: puppeteer page.goto(url) → page.screenshot({...})
        const result = {
            data: '<base64-png-data>',
            format: options.format || 'png',
            width: options.width || this.defaultViewport.width,
            height: options.height || this.defaultViewport.height,
            fullPage: options.fullPage || false,
        };

        this.pool.release(session.id);
        this._log('screenshot', url, session.id);
        return result;
    }

    /**
     * Generate a PDF of a URL.
     * @returns {Promise<{data: string, pages: number, format: string}>}
     */
    async pdf(url, options = {}) {
        const session = this.pool.acquire();
        if (!session) throw new Error('No available sessions');

        console.log(`[BROWSERLESS-OMNI-JS] PDF: ${url}`);
        session.pagesOpened++;

        // Production: page.goto(url) → page.pdf({format: 'A4', ...})
        const result = {
            data: '<base64-pdf-data>',
            pages: 1,
            format: options.paperFormat || 'A4',
            landscape: options.landscape || false,
        };

        this.pool.release(session.id);
        this._log('pdf', url, session.id);
        return result;
    }

    /**
     * Evaluate JavaScript on a page.
     * @returns {Promise<any>} the result of the evaluation
     */
    async evaluate(url, jsCode) {
        const session = this.pool.acquire();
        if (!session) throw new Error('No available sessions');

        console.log(`[BROWSERLESS-OMNI-JS] Evaluate JS on: ${url}`);
        session.pagesOpened++;

        // Production: page.goto(url) → page.evaluate(jsCode)
        const result = { evaluated: true, code: jsCode.substring(0, 50) };

        this.pool.release(session.id);
        this._log('evaluate', url, session.id);
        return result;
    }

    /**
     * Scrape page content (title, text, links).
     * @returns {Promise<{title: string, text: string, links: string[]}>}
     */
    async scrape(url) {
        const session = this.pool.acquire();
        if (!session) throw new Error('No available sessions');

        console.log(`[BROWSERLESS-OMNI-JS] Scrape: ${url}`);
        session.pagesOpened++;

        // Production: page.goto(url) → extract title, text, links
        const result = {
            title: 'Page Title',
            text: 'Page content...',
            links: [],
            timestamp: new Date().toISOString(),
        };

        this.pool.release(session.id);
        this._log('scrape', url, session.id);
        return result;
    }

    _log(type, url, sessionId) {
        this.requestLog.push({ type, url, sessionId, timestamp: new Date() });
    }

    getPoolStats() { return this.pool.getStats(); }
    cleanup() { return this.pool.cleanup(); }
}

module.exports = { BrowserlessWorker, SessionPool };
