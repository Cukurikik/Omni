// ═══════════════════════════════════════════════════════════
// OMNI-STD MATH — OmniMath Module
// ═══════════════════════════════════════════════════════════
// Tensor ops, linear algebra, statistics, activation fns
// Domain: Julia SIMD / Python NumPy / R Stats
// ═══════════════════════════════════════════════════════════

var OmniMath = (function() {

    // ─── Tensor Element-wise Operations ─────────────────
    function tensorOp(op, a, b) {
        // Scalar mode
        if (typeof a === 'number' && typeof b === 'number') {
            switch(op) {
                case '.*': return a * b;
                case '.+': return a + b;
                case '.-': return a - b;
                case './': return b !== 0 ? a / b : Infinity;
                case '.**': return Math.pow(a, b);
                default: return 0;
            }
        }
        // Array/Vector mode
        if (Array.isArray(a) && Array.isArray(b)) {
            var len = Math.min(a.length, b.length);
            var result = [];
            for (var i = 0; i < len; i++) {
                result.push(tensorOp(op, a[i], b[i]));
            }
            return result;
        }
        // Scalar broadcast
        if (Array.isArray(a) && typeof b === 'number') {
            return a.map(function(x) { return tensorOp(op, x, b); });
        }
        if (typeof a === 'number' && Array.isArray(b)) {
            return b.map(function(x) { return tensorOp(op, a, x); });
        }
        return 0;
    }

    // ─── Vector Operations ──────────────────────────────
    function dot(a, b) {
        if (!Array.isArray(a) || !Array.isArray(b)) return a * b;
        var sum = 0;
        for (var i = 0; i < Math.min(a.length, b.length); i++) {
            sum += a[i] * b[i];
        }
        return sum;
    }

    function cross(a, b) {
        if (a.length !== 3 || b.length !== 3) throw new Error('cross() requires 3D vectors');
        return [
            a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0]
        ];
    }

    function magnitude(v) {
        return Math.sqrt(dot(v, v));
    }

    function normalize(v) {
        var mag = magnitude(v);
        if (mag === 0) return v;
        return v.map(function(x) { return x / mag; });
    }

    // ─── Matrix Operations ──────────────────────────────
    function matmul(a, b) {
        var rows = a.length;
        var cols = b[0].length;
        var inner = b.length;
        var result = [];
        for (var i = 0; i < rows; i++) {
            result[i] = [];
            for (var j = 0; j < cols; j++) {
                var sum = 0;
                for (var k = 0; k < inner; k++) {
                    sum += a[i][k] * b[k][j];
                }
                result[i][j] = sum;
            }
        }
        return result;
    }

    function transpose(m) {
        var rows = m.length, cols = m[0].length;
        var result = [];
        for (var j = 0; j < cols; j++) {
            result[j] = [];
            for (var i = 0; i < rows; i++) {
                result[j][i] = m[i][j];
            }
        }
        return result;
    }

    function identity(n) {
        var m = [];
        for (var i = 0; i < n; i++) {
            m[i] = [];
            for (var j = 0; j < n; j++) {
                m[i][j] = (i === j) ? 1 : 0;
            }
        }
        return m;
    }

    // ─── Statistics (R-style) ───────────────────────────
    function sum(arr) {
        var s = 0;
        for (var i = 0; i < arr.length; i++) s += arr[i];
        return s;
    }

    function mean(arr) {
        return arr.length === 0 ? 0 : sum(arr) / arr.length;
    }

    function median(arr) {
        var sorted = arr.slice().sort(function(a, b) { return a - b; });
        var mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid-1] + sorted[mid]) / 2;
    }

    function variance(arr) {
        var m = mean(arr);
        return mean(arr.map(function(x) { return (x - m) * (x - m); }));
    }

    function stddev(arr) {
        return Math.sqrt(variance(arr));
    }

    function min_val(arr) {
        return Math.min.apply(null, arr);
    }

    function max_val(arr) {
        return Math.max.apply(null, arr);
    }

    // ─── Activation Functions (AI/ML) ──────────────────
    function sigmoid(x) {
        if (Array.isArray(x)) return x.map(sigmoid);
        return 1 / (1 + Math.exp(-x));
    }

    function relu(x) {
        if (Array.isArray(x)) return x.map(relu);
        return Math.max(0, x);
    }

    function tanh_fn(x) {
        if (Array.isArray(x)) return x.map(tanh_fn);
        return Math.tanh(x);
    }

    function softmax(arr) {
        var maxVal = max_val(arr);
        var exps = arr.map(function(x) { return Math.exp(x - maxVal); });
        var sumExps = sum(exps);
        return exps.map(function(e) { return e / sumExps; });
    }

    // ─── Utility Math ──────────────────────────────────
    function clamp(val, lo, hi) {
        return Math.max(lo, Math.min(hi, val));
    }

    function lerp(a, b, t) {
        return a + (b - a) * t;
    }

    function range(start, end, step) {
        step = step || 1;
        var result = [];
        for (var i = start; i < end; i += step) result.push(i);
        return result;
    }

    function linspace(start, end, n) {
        var result = [];
        var step = (end - start) / (n - 1);
        for (var i = 0; i < n; i++) result.push(start + step * i);
        return result;
    }

    // ─── Public API ────────────────────────────────────
    return {
        // Tensor
        tensorOp: tensorOp,
        dot: dot,
        cross: cross,
        magnitude: magnitude,
        normalize: normalize,
        // Matrix
        matmul: matmul,
        transpose: transpose,
        identity: identity,
        // Stats
        sum: sum,
        mean: mean,
        median: median,
        variance: variance,
        stddev: stddev,
        min: min_val,
        max: max_val,
        // AI/ML
        sigmoid: sigmoid,
        relu: relu,
        tanh: tanh_fn,
        softmax: softmax,
        // Utility
        clamp: clamp,
        lerp: lerp,
        range: range,
        linspace: linspace,
        // Constants
        PI: Math.PI,
        E: Math.E,
        TAU: Math.PI * 2,
        PHI: (1 + Math.sqrt(5)) / 2,
        EPSILON: Number.EPSILON
    };
})();
