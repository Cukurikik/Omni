// BERTopic Graph Representation
CREATE (t:Topic {id: 1, name: 'Machine Learning', count: 1500})
CREATE (w1:Word {text: 'model', weight: 0.85})
CREATE (w2:Word {text: 'data', weight: 0.72})

CREATE (t)-[:CONTAINS]->(w1)
CREATE (t)-[:CONTAINS]->(w2)

MATCH (t:Topic)-[r:CONTAINS]->(w:Word)
RETURN t, r, w
