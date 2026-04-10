// ═══════════════════════════════════════════════════════════
// OMNI-STD CRYPTO — OmniCrypto
// ═══════════════════════════════════════════════════════════
// UUID, hashing, encoding — pure JS (no Node.js deps)
// ═══════════════════════════════════════════════════════════

var OmniCrypto = (function() {

    // ─── UUID v4 Generator ─────────────────────────────
    function uuid() {
        var hex = '0123456789abcdef';
        var template = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx';
        var result = '';
        for (var i = 0; i < template.length; i++) {
            var c = template[i];
            if (c === 'x') {
                result += hex[Math.floor(Math.random() * 16)];
            } else if (c === 'y') {
                result += hex[(Math.floor(Math.random() * 4) + 8)];
            } else {
                result += c;
            }
        }
        return result;
    }

    // ─── Simple Hash (djb2) ────────────────────────────
    function hash(str) {
        var h = 5381;
        for (var i = 0; i < str.length; i++) {
            h = ((h << 5) + h) + str.charCodeAt(i);
            h = h & h; // Convert to 32bit integer
        }
        return (h >>> 0).toString(16);
    }

    // ─── FNV-1a Hash ───────────────────────────────────
    function fnv1a(str) {
        var h = 0x811c9dc5;
        for (var i = 0; i < str.length; i++) {
            h ^= str.charCodeAt(i);
            h = Math.imul(h, 0x01000193);
        }
        return (h >>> 0).toString(16);
    }

    // ─── Base64 Encoding ───────────────────────────────
    function base64_encode(str) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        var result = '';
        var i = 0;
        while (i < str.length) {
            var a = str.charCodeAt(i++);
            var b = i < str.length ? str.charCodeAt(i++) : 0;
            var c = i < str.length ? str.charCodeAt(i++) : 0;
            var bitmap = (a << 16) | (b << 8) | c;
            result += chars[(bitmap >> 18) & 63] + chars[(bitmap >> 12) & 63];
            result += (i - 2 < str.length) ? chars[(bitmap >> 6) & 63] : '=';
            result += (i - 1 < str.length) ? chars[bitmap & 63] : '=';
        }
        return result;
    }

    function base64_decode(encoded) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        var result = '';
        var clean = encoded.replace(/=+$/, '');
        for (var i = 0; i < clean.length; i += 4) {
            var a = chars.indexOf(clean[i]);
            var b = chars.indexOf(clean[i+1]);
            var c = chars.indexOf(clean[i+2]);
            var d = chars.indexOf(clean[i+3]);
            var bitmap = (a << 18) | (b << 12) | ((c >= 0 ? c : 0) << 6) | (d >= 0 ? d : 0);
            result += String.fromCharCode((bitmap >> 16) & 255);
            if (c >= 0) result += String.fromCharCode((bitmap >> 8) & 255);
            if (d >= 0) result += String.fromCharCode(bitmap & 255);
        }
        return result;
    }

    // ─── Hex Encoding ──────────────────────────────────
    function hex_encode(str) {
        var result = '';
        for (var i = 0; i < str.length; i++) {
            result += str.charCodeAt(i).toString(16).padStart(2, '0');
        }
        return result;
    }

    // ─── Random ────────────────────────────────────────
    function random_int(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function random_bytes(length) {
        var result = [];
        for (var i = 0; i < length; i++) {
            result.push(Math.floor(Math.random() * 256));
        }
        return result;
    }

    function random_string(length) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        var result = '';
        for (var i = 0; i < length; i++) {
            result += chars[Math.floor(Math.random() * chars.length)];
        }
        return result;
    }

    return {
        uuid: uuid,
        hash: hash,
        fnv1a: fnv1a,
        base64_encode: base64_encode,
        base64_decode: base64_decode,
        hex_encode: hex_encode,
        random_int: random_int,
        random_bytes: random_bytes,
        random_string: random_string
    };
})();
