// Create Causal Graph nodes
CREATE (Treatment:Variable {name: 'Treatment', type: 'Intervention'})
CREATE (Outcome:Variable {name: 'Outcome', type: 'Target'})
CREATE (Confounder:Variable {name: 'Confounder', type: 'Unobserved'})

// Define causal relationships
CREATE (Treatment)-[:CAUSES]->(Outcome)
CREATE (Confounder)-[:CAUSES]->(Treatment)
CREATE (Confounder)-[:CAUSES]->(Outcome)

// Query paths
MATCH p=(:Variable {name: 'Treatment'})-[*]->(:Variable {name: 'Outcome'})
RETURN p
