// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Awesome AI Heuristic (OMNI Zero-Mock Implementation)
// Implements A* Pathfinding Heuristic math natively.

export type Result<T> = 
  | { value: T; isOk: true; error: null }
  | { value: null; isOk: false; error: string };

type Point2D = { x: number; y: number };

export class HeuristicEngine {
  
  // Manhattan Distance for grid-based orthogonal movement
  public manhattanDistance(current: Point2D, goal: Point2D): Result<number> {
    if (!current || !goal) {
       return { value: null, isOk: false, error: "Points cannot be null." };
    }
    const dist = Math.abs(current.x - goal.x) + Math.abs(current.y - goal.y);
    return { value: dist, isOk: true, error: null };
  }

  // Euclidean Distance for omni-directional free movement
  public euclideanDistance(current: Point2D, goal: Point2D): Result<number> {
    if (!current || !goal) {
       return { value: null, isOk: false, error: "Points cannot be null." };
    }
    const dx = current.x - goal.x;
    const dy = current.y - goal.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    return { value: dist, isOk: true, error: null };
  }
  
  // Chebyshev Distance for grids allowing diagonal movement (8-way)
  public chebyshevDistance(current: Point2D, goal: Point2D): Result<number> {
    if (!current || !goal) {
       return { value: null, isOk: false, error: "Points cannot be null." };
    }
    const dx = Math.abs(current.x - goal.x);
    const dy = Math.abs(current.y - goal.y);
    const dist = Math.max(dx, dy);
    return { value: dist, isOk: true, error: null };
  }
}
