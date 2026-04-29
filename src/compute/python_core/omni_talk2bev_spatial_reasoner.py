# Omni Talk2BEV Spatial Reasoner
# Ref: llmbev/talk2bev — ICRA'24
import math
from typing import Dict, List, Tuple
def euclidean_distance(p1: Tuple[float,float], p2: Tuple[float,float]) -> float:
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
def spatial_query(objects: List[Dict], query_point: Tuple[float,float], radius: float) -> List[Dict]:
    return [o for o in objects if euclidean_distance((o.get("x",0),o.get("y",0)), query_point) <= radius]
def bev_grid_occupancy(objects: List[Dict], grid_size: int = 100, cell_size: float = 0.5) -> List[List[int]]:
    grid = [[0]*grid_size for _ in range(grid_size)]
    for o in objects:
        gx = int(o.get("x",0)/cell_size) % grid_size; gy = int(o.get("y",0)/cell_size) % grid_size
        grid[gy][gx] = 1
    return grid
