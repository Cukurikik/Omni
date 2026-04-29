class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class TorusGeometry:
    def __init__(self):
        pass

    def compute_tpu_pod_distance(self, node_a: tuple, node_b: tuple, grid_size: tuple) -> OmniResult:
        if len(node_a) != 3 or len(node_b) != 3 or len(grid_size) != 3:
            return OmniResult(error="Coordinates must be 3D (x, y, z)")

        # Deterministic calculation of 3D Torus interconnect distances
        # TPUs are wired in a wrapping 3D grid. This calculates the shortest path between any two TPU cores.
        try:
            distance = 0
            for i in range(3):
                if node_a[i] < 0 or node_b[i] < 0 or grid_size[i] <= 0:
                    return OmniResult(error="Coordinates and grid sizes must be positive")
                
                # Direct distance
                direct = abs(node_a[i] - node_b[i])
                # Wrap-around distance (Torus topology)
                wrapped = grid_size[i] - direct
                
                # Shortest path on this axis
                distance += min(direct, wrapped)
            
            return OmniResult(value=distance)
        except Exception as e:
            return OmniResult(error=str(e))
