# Omni MMStar Vision HUD (GDScript)
# Game Engine Layer for Godot: VLM vision marker overlays.

extends Control
class_name OmniVisionHUD

var active_markers: Array = []

func _ready() -> void:
    set_process(true)

# Monadic-like error dictionary return
func register_vision_marker(id: String, screen_pos: Vector2) -> Dictionary:
    if id == "":
        return {"success": false, "error": "Invalid marker ID"}
        
    var marker_data = {"id": id, "pos": screen_pos}
    active_markers.append(marker_data)
    
    queue_redraw()
    return {"success": true, "error": ""}

func _draw() -> void:
    for marker in active_markers:
        draw_circle(marker["pos"], 5.0, Color.GREEN)
