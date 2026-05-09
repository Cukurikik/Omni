extends Node2D
# OMNI MOTHER: GDScript Network Graph Visualizer (Production Grade)
# Renders nodes and connections dynamically based on MoE routing probabilities.

var expert_nodes = []

func _ready():
    print("[OMNI GODOT] Initializing MoE Network Graph...")
    for i in range(16):
        var expert = load("res://OmniExpertNode.tscn").instance()
        expert.position = Vector2(100 + (i % 4) * 80, 100 + (i / 4) * 80)
        add_child(expert)
        expert_nodes.append(expert)

func update_routing(routing_tensor_data: Array):
    # routing_tensor_data represents an array of 16 probabilities
    for i in range(expert_nodes.size()):
        if i < routing_tensor_data.size():
            var prob = routing_tensor_data[i]
            expert_nodes[i].set_activation_level(prob)