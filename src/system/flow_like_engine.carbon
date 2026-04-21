// ===========================================================================
// OMNI SYSTEM LAYER — FLOW-LIKE MEDIA PROCESSING KERNEL
// ===========================================================================
// Source Paradigm : nicehash/flow-like
// Domain Layer   : System (Modern C++ successor, interface-based)
// Language        : Carbon
// Function        : High-performance media processing DAG engine with typed
//                   node graph, pin connections, execution scheduler, and
//                   frame-level pipeline for video/audio transformation
// ===========================================================================

package OmniFlow;

// ---- Core Enums -----------------------------------------------------------

choice PinType {
    Video,
    Audio,
    Data,
    Control,
    Text,
}

choice NodeState {
    Idle,
    Running,
    Completed,
    Error,
    Disabled,
}

// ---- Pin Definition (node input/output ports) -----------------------------

class Pin {
    var name: String;
    var pin_type: PinType;
    var is_input: bool;
    var is_connected: bool;
    var connected_to_node: String;
    var connected_to_pin: String;

    fn Create(n: String, t: PinType, input: bool) -> Pin {
        return {
            .name = n,
            .pin_type = t,
            .is_input = input,
            .is_connected = false,
            .connected_to_node = "",
            .connected_to_pin = "",
        };
    }
}

// ---- Node Base (processing unit in the DAG) -------------------------------

class FlowNode {
    var id: String;
    var label: String;
    var state: NodeState;
    var inputs: Array(Pin);
    var outputs: Array(Pin);
    var params: Map(String, String);
    var process_time_ms: f64;

    fn Create(node_id: String, node_label: String) -> FlowNode {
        return {
            .id = node_id,
            .label = node_label,
            .state = NodeState.Idle,
            .inputs = (),
            .outputs = (),
            .params = {},
            .process_time_ms = 0.0,
        };
    }

    fn AddInput(self: Self*, name: String, pin_type: PinType) {
        self->inputs.push(Pin.Create(name, pin_type, true));
    }

    fn AddOutput(self: Self*, name: String, pin_type: PinType) {
        self->outputs.push(Pin.Create(name, pin_type, false));
    }

    fn SetParam(self: Self*, key: String, value: String) {
        self->params[key] = value;
    }
}

// ---- Connection (edge between pins) ---------------------------------------

class FlowEdge {
    var from_node_id: String;
    var from_pin: String;
    var to_node_id: String;
    var to_pin: String;

    fn Create(from_n: String, from_p: String, to_n: String, to_p: String) -> FlowEdge {
        return {
            .from_node_id = from_n,
            .from_pin = from_p,
            .to_node_id = to_n,
            .to_pin = to_p,
        };
    }
}

// ---- DAG Graph (the full processing pipeline) -----------------------------

class FlowGraph {
    var name: String;
    var nodes: Map(String, FlowNode);
    var edges: Array(FlowEdge);
    var execution_order: Array(String);

    fn Create(graph_name: String) -> FlowGraph {
        return {
            .name = graph_name,
            .nodes = {},
            .edges = (),
            .execution_order = (),
        };
    }

    fn AddNode(self: Self*, node: FlowNode) {
        Print("[FLOW-OMNI-CARBON] Added node: {node.label} ({node.id})");
        self->nodes[node.id] = node;
    }

    fn Connect(self: Self*, from_id: String, from_pin: String,
               to_id: String, to_pin: String) -> bool {
        // Validate nodes exist
        if (not self->nodes.contains(from_id) or not self->nodes.contains(to_id)) {
            Print("[FLOW-OMNI-CARBON] ERROR: Node not found in graph.");
            return false;
        }

        let edge = FlowEdge.Create(from_id, from_pin, to_id, to_pin);
        self->edges.push(edge);
        Print("[FLOW-OMNI-CARBON] Connected: {from_id}.{from_pin} → {to_id}.{to_pin}");
        return true;
    }

    // Topological sort for execution order (Kahn's algorithm)
    fn ComputeExecutionOrder(self: Self*) -> bool {
        Print("[FLOW-OMNI-CARBON] Computing topological execution order...");

        var in_degree: Map(String, i32) = {};
        for (node_id in self->nodes.keys()) {
            in_degree[node_id] = 0;
        }

        for (edge in self->edges) {
            in_degree[edge.to_node_id] += 1;
        }

        var queue: Array(String) = ();
        for (node_id in in_degree.keys()) {
            if (in_degree[node_id] == 0) {
                queue.push(node_id);
            }
        }

        self->execution_order = ();
        while (queue.size() > 0) {
            let current = queue.pop_front();
            self->execution_order.push(current);

            for (edge in self->edges) {
                if (edge.from_node_id == current) {
                    in_degree[edge.to_node_id] -= 1;
                    if (in_degree[edge.to_node_id] == 0) {
                        queue.push(edge.to_node_id);
                    }
                }
            }
        }

        let valid = self->execution_order.size() == self->nodes.size();
        if (valid) {
            Print("[FLOW-OMNI-CARBON] Execution order computed ({self->execution_order.size()} nodes).");
        } else {
            Print("[FLOW-OMNI-CARBON] ERROR: Cycle detected in graph!");
        }
        return valid;
    }

    fn Execute(self: Self*) {
        Print("[FLOW-OMNI-CARBON] ═══ Executing graph: {self->name} ═══");

        if (self->execution_order.size() == 0) {
            self->ComputeExecutionOrder();
        }

        for (node_id in self->execution_order) {
            var node = self->nodes[node_id];
            node.state = NodeState.Running;
            Print("[FLOW-OMNI-CARBON]   Processing: {node.label}");
            // Production: dispatch to node-type-specific processor
            node.state = NodeState.Completed;
        }

        Print("[FLOW-OMNI-CARBON] ═══ Graph execution complete ═══");
    }
}
