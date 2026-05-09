extends Node
class_name OmniTransformerClient

# OMNI Game Layer
# Godot GDScript node that interfaces with the OMNI local UDP socket
# to stream inference data (NPC dialogues, procedural generation) without stalling the game thread.

var udp_peer := PacketPeerUDP.new()
var is_connected := false

signal inference_received(payload)

func _ready() -> void:
    var err = udp_peer.connect_to_host("127.0.0.1", 9095)
    if err == OK:
        is_connected = true
        print("OMNI Godot Module: Connected to Omni Inference Engine.")
    else:
        push_error("OMNI Godot Module: Failed to connect to Omni Engine.")

func _process(_delta: float) -> void:
    if not is_connected:
        return
        
    # Non-blocking poll for incoming transformer responses
    while udp_peer.get_available_packet_count() > 0:
        var packet = udp_peer.get_packet()
        var response_str = packet.get_string_from_utf8()
        
        var json = JSON.new()
        var error = json.parse(response_str)
        if error == OK:
            var data = json.get_data()
            emit_signal("inference_received", data)
        else:
            push_error("OMNI Godot Module: JSON Parse Error on incoming inference.")

# Sends a request to the Omni Engine for generative tasks
func request_npc_dialogue(npc_id: String, context_prompt: String) -> void:
    if not is_connected:
        return
        
    var request = {
        "action": "generate_dialogue",
        "npc_id": npc_id,
        "context": context_prompt
    }
    
    var json_string = JSON.stringify(request)
    var packet_data = json_string.to_utf8_buffer()
    
    udp_peer.put_packet(packet_data)
    print("OMNI Godot Module: Dispatched request for NPC ", npc_id)
