// ═══════════════════════════════════════════════════════════
// OMNI-STD UI — OmniUI (Component & Virtual DOM)
// ═══════════════════════════════════════════════════════════
// TypeScript/Swift-inspired component system
// ═══════════════════════════════════════════════════════════

var OmniUI = (function() {

    var _components = {};
    var _renderCount = 0;

    // ─── Virtual DOM Node ───────────────────────────────
    function createElement(tag, props, children) {
        _renderCount++;
        return {
            __omni_vnode: true,
            tag: tag,
            props: props || {},
            children: children || [],
            key: props && props.key ? props.key : null,
            id: 'vnode_' + _renderCount
        };
    }

    // ─── Render VNode → HTML String ─────────────────────
    function renderToString(vnode) {
        if (typeof vnode === 'string' || typeof vnode === 'number') {
            return String(vnode);
        }
        if (!vnode || !vnode.__omni_vnode) {
            return String(vnode);
        }

        var tag = vnode.tag;
        var props = vnode.props || {};
        var children = vnode.children || [];

        // Build attributes
        var attrs = '';
        var propKeys = Object.keys(props);
        for (var i = 0; i < propKeys.length; i++) {
            var key = propKeys[i];
            if (key === 'key' || key === 'children' || typeof props[key] === 'function') continue;
            attrs += ' ' + key + '="' + String(props[key]) + '"';
        }

        // Self-closing tags
        var selfClosing = ['img', 'br', 'hr', 'input', 'meta', 'link'];
        if (selfClosing.indexOf(tag) !== -1) {
            return '<' + tag + attrs + ' />';
        }

        // Render children
        var childHtml = '';
        for (var j = 0; j < children.length; j++) {
            childHtml += renderToString(children[j]);
        }

        return '<' + tag + attrs + '>' + childHtml + '</' + tag + '>';
    }

    // ─── Component Registry ─────────────────────────────
    function defineComponent(name, renderFn) {
        _components[name] = renderFn;
    }

    function renderComponent(name, props) {
        if (!_components[name]) {
            return createElement('div', { class: 'error' }, ['Component not found: ' + name]);
        }
        return _components[name](props || {});
    }

    // ─── State Management (basic) ───────────────────────
    function createState(initialValue) {
        var value = initialValue;
        return {
            get: function() { return value; },
            set: function(newValue) { value = newValue; },
            update: function(fn) { value = fn(value); }
        };
    }

    // ─── Style Builder ──────────────────────────────────
    function style(obj) {
        var parts = [];
        var keys = Object.keys(obj);
        for (var i = 0; i < keys.length; i++) {
            var cssKey = keys[i].replace(/([A-Z])/g, '-$1').toLowerCase();
            parts.push(cssKey + ': ' + obj[keys[i]]);
        }
        return parts.join('; ');
    }

    // ─── CSS Class Builder ──────────────────────────────
    function classNames() {
        var result = [];
        for (var i = 0; i < arguments.length; i++) {
            var arg = arguments[i];
            if (typeof arg === 'string') {
                result.push(arg);
            } else if (typeof arg === 'object' && arg !== null) {
                var keys = Object.keys(arg);
                for (var j = 0; j < keys.length; j++) {
                    if (arg[keys[j]]) result.push(keys[j]);
                }
            }
        }
        return result.join(' ');
    }

    return {
        createElement: createElement,
        h: createElement,
        renderToString: renderToString,
        defineComponent: defineComponent,
        renderComponent: renderComponent,
        createState: createState,
        style: style,
        classNames: classNames,
        getRenderCount: function() { return _renderCount; }
    };
})();

// Shorthand
var h = OmniUI.h;
