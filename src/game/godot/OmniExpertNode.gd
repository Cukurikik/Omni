extends Sprite
# OMNI MOTHER: GDScript Expert Node Visuals (Production Grade)

var current_activation: float = 0.0

func _ready():
    # Initialize basic node properties
    modulate = Color(1.0, 1.0, 1.0, 0.5)
    print("[OMNI GODOT] Expert Node spawned.")

func set_activation_level(level: float):
    current_activation = clamp(level, 0.0, 1.0)
    
    # Glow effect based on activation
    if current_activation > 0.5:
        modulate = Color(1.0, 0.5, 0.8, 1.0) # Moebuntu Pink glow
        scale = Vector2(1.2, 1.2)
    else:
        modulate = Color(1.0, 1.0, 1.0, 0.5 + (current_activation * 0.5))
        scale = Vector2(1.0, 1.0)
