// Omni SIM-CoT Traversal (Gremlin / Groovy)
// Database Layer: Graph traversal for implicit chain of thought trajectories.

g.V().hasLabel('reasoning_step')
 .has('temperature', P.gt(0.0))
 .outE('implicit_link')
 .inV()
 .path()
 .by('step_id')
 .limit(100)
 .toList()
