extends Node
class_name OmniPhysicsSync

# Omni Godot GDScript Core
# Deterministic server-authoritative physics synchronization

func sync_transform(node: Node3D, server_position: Vector3, server_rotation: Vector3) -> bool:
    if node == null:
        return false # Emulating Monadic Error
        
    var distance_sq = node.global_position.distance_squared_to(server_position)
    
    # Snap if divergence is too high, otherwise interpolate
    if distance_sq > 10.0:
        node.global_position = server_position
        node.global_rotation = server_rotation
    else:
        node.global_position = node.global_position.lerp(server_position, 0.5)
        
    return true
