import omni

def spawn_ray_actor(actor_class: type) -> omni.Result:
    return omni.Result.Ok(actor_class())
