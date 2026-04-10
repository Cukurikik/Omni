// ═══════════════════════════════════════════════════════════
// OMNI-STD TIME — Scheduling & Timing
// ═══════════════════════════════════════════════════════════
// setTimeout/setInterval polyfills for V8 sandbox
// Go-style spawn → immediate execution in sync V8
// ═══════════════════════════════════════════════════════════

// V8 Isolate tidak punya event loop — semua di-eksekusi synchronous
function setTimeout(fn, _delay) { 
    try { fn(); } catch(e) { __omni_errors.push('setTimeout error: ' + e.message); }
}

function setInterval(fn, _delay) { 
    try { fn(); } catch(e) { __omni_errors.push('setInterval error: ' + e.message); }
}

function clearTimeout() {}
function clearInterval() {}

var OmniTime = (function() {
    var _start = Date.now();

    function now() { return Date.now(); }
    function elapsed() { return Date.now() - _start; }
    function timestamp() { return new Date().toISOString(); }
    
    function measure(label, fn) {
        var start = Date.now();
        var result = fn();
        var duration = Date.now() - start;
        print('[BENCH] ' + label + ': ' + duration + 'ms');
        return result;
    }

    function sleep(ms) {
        // Synchronous sleep in V8 (blocking)
        var end = Date.now() + ms;
        while (Date.now() < end) {}
    }

    function format(date, pattern) {
        var d = new Date(date);
        var map = {
            'YYYY': d.getFullYear(),
            'MM': String(d.getMonth() + 1).padStart(2, '0'),
            'DD': String(d.getDate()).padStart(2, '0'),
            'HH': String(d.getHours()).padStart(2, '0'),
            'mm': String(d.getMinutes()).padStart(2, '0'),
            'ss': String(d.getSeconds()).padStart(2, '0')
        };
        var result = pattern;
        var keys = Object.keys(map);
        for (var i = 0; i < keys.length; i++) {
            result = result.replace(keys[i], map[keys[i]]);
        }
        return result;
    }

    return {
        now: now,
        elapsed: elapsed,
        timestamp: timestamp,
        measure: measure,
        sleep: sleep,
        format: format
    };
})();
