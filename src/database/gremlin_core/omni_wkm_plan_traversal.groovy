// Omni WKM Plan Traversal (Gremlin)
// Database Layer: Graph traversal for agent planning world model.
// Ref: zjunlp/WKM

g.V().hasLabel('task_goal')
 .outE('decomposes_to')
 .inV().hasLabel('sub_task')
 .order().by('difficulty', Order.asc)
 .path()
 .by('name')
 .limit(50)
 .toList()
