// ═══════════════════════════════════════════════════════════
// OMNI-STD STRING — OmniString
// ═══════════════════════════════════════════════════════════
// String manipulation utilities
// ═══════════════════════════════════════════════════════════

var OmniString = (function() {

    function capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function camelCase(str) {
        return str.replace(/[-_\s]+(.)?/g, function(_, c) { return c ? c.toUpperCase() : ''; });
    }

    function snakeCase(str) {
        return str.replace(/([A-Z])/g, '_$1').toLowerCase().replace(/^_/, '');
    }

    function kebabCase(str) {
        return str.replace(/([A-Z])/g, '-$1').toLowerCase().replace(/^-/, '');
    }

    function truncate(str, len, suffix) {
        suffix = suffix || '...';
        if (str.length <= len) return str;
        return str.slice(0, len - suffix.length) + suffix;
    }

    function pad_left(str, len, char) {
        char = char || ' ';
        while (str.length < len) str = char + str;
        return str;
    }

    function pad_right(str, len, char) {
        char = char || ' ';
        while (str.length < len) str = str + char;
        return str;
    }

    function repeat(str, n) {
        var result = '';
        for (var i = 0; i < n; i++) result += str;
        return result;
    }

    function reverse(str) {
        return str.split('').reverse().join('');
    }

    function contains(str, sub) {
        return str.indexOf(sub) !== -1;
    }

    function starts_with(str, prefix) {
        return str.indexOf(prefix) === 0;
    }

    function ends_with(str, suffix) {
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
    }

    function count(str, sub) {
        var count = 0, pos = 0;
        while ((pos = str.indexOf(sub, pos)) !== -1) {
            count++;
            pos += sub.length;
        }
        return count;
    }

    function words(str) {
        return str.trim().split(/\s+/);
    }

    function lines(str) {
        return str.split(/\r?\n/);
    }

    function template(str, vars) {
        return str.replace(/\{\{(\w+)\}\}/g, function(_, key) {
            return vars.hasOwnProperty(key) ? vars[key] : '{{' + key + '}}';
        });
    }

    function is_empty(str) {
        return !str || str.trim().length === 0;
    }

    function slugify(str) {
        return str.toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    return {
        capitalize: capitalize,
        camelCase: camelCase,
        snakeCase: snakeCase,
        kebabCase: kebabCase,
        truncate: truncate,
        padLeft: pad_left,
        padRight: pad_right,
        repeat: repeat,
        reverse: reverse,
        contains: contains,
        startsWith: starts_with,
        endsWith: ends_with,
        count: count,
        words: words,
        lines: lines,
        template: template,
        isEmpty: is_empty,
        slugify: slugify
    };
})();
