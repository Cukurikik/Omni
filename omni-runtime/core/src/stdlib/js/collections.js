// ═══════════════════════════════════════════════════════════
// OMNI-STD COLLECTIONS — Array, Map, Set Utilities
// ═══════════════════════════════════════════════════════════
// Ruby/Python-inspired collection helpers
// ═══════════════════════════════════════════════════════════

var OmniCollections = (function() {

    // ─── Array Utilities ────────────────────────────────
    function chunk(arr, size) {
        var result = [];
        for (var i = 0; i < arr.length; i += size) {
            result.push(arr.slice(i, i + size));
        }
        return result;
    }

    function flatten(arr) {
        var result = [];
        for (var i = 0; i < arr.length; i++) {
            if (Array.isArray(arr[i])) {
                var inner = flatten(arr[i]);
                for (var j = 0; j < inner.length; j++) result.push(inner[j]);
            } else {
                result.push(arr[i]);
            }
        }
        return result;
    }

    function unique(arr) {
        var seen = {};
        var result = [];
        for (var i = 0; i < arr.length; i++) {
            var key = JSON.stringify(arr[i]);
            if (!seen[key]) {
                seen[key] = true;
                result.push(arr[i]);
            }
        }
        return result;
    }

    function zip(a, b) {
        var len = Math.min(a.length, b.length);
        var result = [];
        for (var i = 0; i < len; i++) {
            result.push([a[i], b[i]]);
        }
        return result;
    }

    function unzip(pairs) {
        var a = [], b = [];
        for (var i = 0; i < pairs.length; i++) {
            a.push(pairs[i][0]);
            b.push(pairs[i][1]);
        }
        return [a, b];
    }

    function group_by(arr, fn) {
        var groups = {};
        for (var i = 0; i < arr.length; i++) {
            var key = fn(arr[i]);
            if (!groups[key]) groups[key] = [];
            groups[key].push(arr[i]);
        }
        return groups;
    }

    function partition(arr, fn) {
        var pass = [], fail = [];
        for (var i = 0; i < arr.length; i++) {
            if (fn(arr[i])) pass.push(arr[i]);
            else fail.push(arr[i]);
        }
        return [pass, fail];
    }

    function take(arr, n) { return arr.slice(0, n); }
    function drop(arr, n) { return arr.slice(n); }
    function first(arr) { return arr.length > 0 ? arr[0] : undefined; }
    function last(arr) { return arr.length > 0 ? arr[arr.length - 1] : undefined; }

    function compact(arr) {
        return arr.filter(function(x) { return x != null && x !== false && x !== '' && x === x; });
    }

    function sum(arr) {
        var s = 0;
        for (var i = 0; i < arr.length; i++) s += arr[i];
        return s;
    }

    function count_by(arr, fn) {
        var counts = {};
        for (var i = 0; i < arr.length; i++) {
            var key = fn(arr[i]);
            counts[key] = (counts[key] || 0) + 1;
        }
        return counts;
    }

    function sort_by(arr, fn) {
        return arr.slice().sort(function(a, b) {
            var va = fn(a), vb = fn(b);
            return va < vb ? -1 : va > vb ? 1 : 0;
        });
    }

    // ─── HashMap Utilities ──────────────────────────────
    function map_values(obj, fn) {
        var result = {};
        var keys = Object.keys(obj);
        for (var i = 0; i < keys.length; i++) {
            result[keys[i]] = fn(obj[keys[i]], keys[i]);
        }
        return result;
    }

    function map_keys(obj, fn) {
        var result = {};
        var keys = Object.keys(obj);
        for (var i = 0; i < keys.length; i++) {
            result[fn(keys[i])] = obj[keys[i]];
        }
        return result;
    }

    function pick(obj, keys) {
        var result = {};
        for (var i = 0; i < keys.length; i++) {
            if (obj.hasOwnProperty(keys[i])) result[keys[i]] = obj[keys[i]];
        }
        return result;
    }

    function omit(obj, keys) {
        var result = {};
        var exclude = {};
        for (var i = 0; i < keys.length; i++) exclude[keys[i]] = true;
        var allKeys = Object.keys(obj);
        for (var j = 0; j < allKeys.length; j++) {
            if (!exclude[allKeys[j]]) result[allKeys[j]] = obj[allKeys[j]];
        }
        return result;
    }

    function merge() {
        var result = {};
        for (var i = 0; i < arguments.length; i++) {
            var obj = arguments[i];
            var keys = Object.keys(obj);
            for (var j = 0; j < keys.length; j++) {
                result[keys[j]] = obj[keys[j]];
            }
        }
        return result;
    }

    return {
        chunk: chunk, flatten: flatten, unique: unique,
        zip: zip, unzip: unzip, group_by: group_by,
        partition: partition, take: take, drop: drop,
        first: first, last: last, compact: compact,
        sum: sum, count_by: count_by, sort_by: sort_by,
        map_values: map_values, map_keys: map_keys,
        pick: pick, omit: omit, merge: merge
    };
})();
