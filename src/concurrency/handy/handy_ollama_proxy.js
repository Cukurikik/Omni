// OMNI Concurrency Layer: handy_ollama_proxy.js
// Handles non-blocking relay to local Ollama instance for Handy Ollama.
// Event Loop Bound: Limits in-flight requests to 50 concurrent.

const MAX_CONCURRENT_OLLAMA_REQS = 50;
let inFlightRequests = 0;

class OmniError extends Error {
    constructor(code, message) {
        super(message);
        this.code = code;
    }
}

class OmniResult {
    constructor(data, error) {
        this.data = data;
        this.error = error;
    }
}

/**
 * Routes prompt to local Ollama with strict event loop bounds
 */
async function routePromptToOllama(model, prompt) {
    if (inFlightRequests >= MAX_CONCURRENT_OLLAMA_REQS) {
        return new OmniResult(null, new OmniError(1, "Ollama request bound exceeded (50)."));
    }

    inFlightRequests++;
    try {
        // Native Fetch equivalent in OMNI V8 context
        const response = await fetch("http://127.0.0.1:11434/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ model, prompt, stream: false })
        });

        if (!response.ok) {
            return new OmniResult(null, new OmniError(2, `Ollama API Error: ${response.status}`));
        }

        const data = await response.json();
        return new OmniResult(data.response, null);
    } catch (err) {
        return new OmniResult(null, new OmniError(3, err.message));
    } finally {
        inFlightRequests--;
    }
}

export { routePromptToOllama, OmniResult, OmniError };
