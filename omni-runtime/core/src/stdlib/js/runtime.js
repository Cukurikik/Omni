// ═══════════════════════════════════════════════════════════
// OMNI-STD RUNTIME — Core I/O & Type System
// ═══════════════════════════════════════════════════════════
// Modul inti: output capture, print(), console, type helpers
// ═══════════════════════════════════════════════════════════

'use strict';

var __omni_output = [];
var __omni_errors = [];
var __omni_version = '2.0.0';

// ─── print() — Fungsi output utama OMNI ─────────────────
function print() {
    var args = [];
    for (var i = 0; i < arguments.length; i++) {
        var a = arguments[i];
        if (a === null) {
            args.push('null');
        } else if (a === undefined) {
            args.push('undefined');
        } else if (typeof a === 'object') {
            try {
                args.push(JSON.stringify(a, null, 2));
            } catch(e) {
                args.push('[Object]');
            }
        } else {
            args.push(String(a));
        }
    }
    __omni_output.push(args.join(' '));
}

// ─── println() — print dengan newline eksplisit ─────────
function println() {
    print.apply(null, arguments);
}

// ─── console — Standar JS Console API ───────────────────
var console = {
    log: print,
    info: print,
    warn: function() {
        var args = Array.prototype.slice.call(arguments);
        __omni_output.push('[WARN] ' + args.join(' '));
    },
    error: function() {
        var args = Array.prototype.slice.call(arguments);
        var msg = '[ERROR] ' + args.join(' ');
        __omni_output.push(msg);
        __omni_errors.push(msg);
    },
    debug: function() {
        var args = Array.prototype.slice.call(arguments);
        __omni_output.push('[DEBUG] ' + args.join(' '));
    },
    table: function(data) {
        if (Array.isArray(data)) {
            data.forEach(function(row, i) {
                print('[' + i + ']', row);
            });
        } else if (typeof data === 'object') {
            Object.keys(data).forEach(function(key) {
                print(key + ':', data[key]);
            });
        }
    },
    time: function() {},
    timeEnd: function() {},
    assert: function(condition, msg) {
        if (!condition) {
            __omni_errors.push('Assertion failed: ' + (msg || ''));
            throw new Error('Assertion failed: ' + (msg || ''));
        }
    }
};

// ─── assert_eq() — OMNI macro ──────────────────────────
function assert_eq(a, b) {
    if (a !== b) {
        var msg = 'assert_eq failed: ' + JSON.stringify(a) + ' !== ' + JSON.stringify(b);
        __omni_errors.push(msg);
        throw new Error(msg);
    }
}

function assert_ne(a, b) {
    if (a === b) {
        var msg = 'assert_ne failed: values are equal: ' + JSON.stringify(a);
        __omni_errors.push(msg);
        throw new Error(msg);
    }
}

// ─── typeof helpers ────────────────────────────────────

function omni_typeof(val) {
    if (val === null) return 'Null';
    if (val === undefined) return 'Undefined';
    if (Array.isArray(val)) return 'Array';
    var t = typeof val;
    return t.charAt(0).toUpperCase() + t.slice(1);
}

function is_string(val) { return typeof val === 'string'; }
function is_number(val) { return typeof val === 'number' && !isNaN(val); }
function is_bool(val) { return typeof val === 'boolean'; }
function is_array(val) { return Array.isArray(val); }
function is_object(val) { return typeof val === 'object' && val !== null && !Array.isArray(val); }
function is_function(val) { return typeof val === 'function'; }
function is_null(val) { return val === null; }
function is_undefined(val) { return val === undefined; }

// ─── OmniRuntime helpers ────────────────────────────────────
var OmniRuntime = {
    unwrap: function(result) {
        if (result && typeof result === 'object' && 'Ok' in result) {
            return result.Ok;
        }
        if (result && typeof result === 'object' && 'Err' in result) {
            __omni_errors.push(String(result.Err));
            throw new Error(result.Err);
        }
        if (result instanceof Error) {
            __omni_errors.push(result.message);
            throw result;
        }
        return result; // Fallback for raw values
    }
};
