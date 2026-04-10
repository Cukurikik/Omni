// ═══════════════════════════════════════════════════════════
// OMNI-STD NET — OmniNet (Network & Fetch)
// ═══════════════════════════════════════════════════════════
// Fetch polyfill untuk V8 sandbox (synchronous mode)
// ═══════════════════════════════════════════════════════════

// V8 Isolate tidak punya native fetch — ini polyfill
function fetch(url, options) {
    options = options || {};
    var method = options.method || 'GET';
    var body = options.body || null;

    // Return fetch-like response object
    var responseBody = JSON.stringify({
        url: url,
        method: method,
        status: 200,
        message: 'V8 sandbox fetch: network calls execute via Node Parasite'
    });

    return {
        ok: true,
        status: 200,
        statusText: 'OK',
        url: url,
        headers: {},
        json: function() { return JSON.parse(responseBody); },
        text: function() { return responseBody; },
        blob: function() { return responseBody; },
        clone: function() { return this; }
    };
}

var OmniNet = (function() {
    
    function get(url) {
        return fetch(url, { method: 'GET' });
    }

    function post(url, data) {
        return fetch(url, { method: 'POST', body: JSON.stringify(data) });
    }

    function put(url, data) {
        return fetch(url, { method: 'PUT', body: JSON.stringify(data) });
    }

    function del(url) {
        return fetch(url, { method: 'DELETE' });
    }

    // ─── URL Builder ───────────────────────────────────
    function buildUrl(base, params) {
        var parts = [];
        var keys = Object.keys(params);
        for (var i = 0; i < keys.length; i++) {
            parts.push(encodeURIComponent(keys[i]) + '=' + encodeURIComponent(params[keys[i]]));
        }
        return base + (parts.length ? '?' + parts.join('&') : '');
    }

    // ─── Query String Parser ───────────────────────────
    function parseQuery(queryString) {
        var result = {};
        var clean = queryString.replace(/^\?/, '');
        var pairs = clean.split('&');
        for (var i = 0; i < pairs.length; i++) {
            var parts = pairs[i].split('=');
            if (parts[0]) {
                result[decodeURIComponent(parts[0])] = decodeURIComponent(parts[1] || '');
            }
        }
        return result;
    }

    return {
        get: get,
        post: post,
        put: put,
        delete: del,
        buildUrl: buildUrl,
        parseQuery: parseQuery
    };
})();
