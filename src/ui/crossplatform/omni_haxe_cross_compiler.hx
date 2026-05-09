// OMNI UI & Cross-Platform Layer
// Haxe implementation for defining dynamic UI structures that compile identically to Flash, JS, C++, and JVM.

package omni.ui;

typedef UINode = {
    var id: String;
    var type: String;
    var children: Array<UINode>;
    var properties: Dynamic;
}

class OmniHaxeRenderer {
    
    // Parses a declarative UI state from the Omni Transformer engine
    public static function renderTree(jsonPayload: String): UINode {
        var rawData = haxe.Json.parse(jsonPayload);
        return buildNode(rawData);
    }
    
    private static function buildNode(data: Dynamic): UINode {
        var node: UINode = {
            id: data.id != null ? data.id : "gen_" + Std.random(10000),
            type: data.type,
            children: [],
            properties: data.props
        };
        
        if (data.children != null) {
            var kids: Array<Dynamic> = data.children;
            for (k in kids) {
                node.children.push(buildNode(k));
            }
        }
        
        trace("OMNI Haxe: Bound UI Node " + node.id + " of type " + node.type);
        return node;
    }
    
    // Dispatches a UI interaction back to the Omni Native core
    public static function dispatchEvent(nodeId: String, eventType: String, payload: Dynamic) {
        var eventStr = haxe.Json.stringify({
            node: nodeId,
            event: eventType,
            data: payload
        });
        
        #if cpp
        // Native C++ C-ABI call
        OmniNativeBridge.sendEvent(eventStr);
        #elseif js
        // WebAssembly JS interop
        js.Syntax.code("window.OmniWasm.sendEvent({0})", eventStr);
        #else
        trace("OMNI Fallback Event Dispatch: " + eventStr);
        #end
    }
}
