// Mathematics for Machine Learning Dependency Graph
CREATE (linalg:Concept {name: 'Linear Algebra'})
CREATE (calc:Concept {name: 'Calculus'})
CREATE (prob:Concept {name: 'Probability Theory'})
CREATE (opt:Concept {name: 'Continuous Optimization'})
CREATE (ml:Concept {name: 'Machine Learning Models'})

CREATE (calc)-[:PREREQUISITE_FOR]->(opt)
CREATE (linalg)-[:PREREQUISITE_FOR]->(opt)
CREATE (prob)-[:PREREQUISITE_FOR]->(ml)
CREATE (opt)-[:PREREQUISITE_FOR]->(ml)

MATCH (p)-[:PREREQUISITE_FOR]->(c:Concept {name: 'Continuous Optimization'})
RETURN p.name
