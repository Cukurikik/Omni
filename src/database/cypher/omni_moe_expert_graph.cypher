// OMNI MOTHER: Cypher Query for Expert Tracking
// Database & Query Layer: Tracks topological distance between MoE Experts

CREATE (e1:Expert {id: 'expert-01', type: 'mlp', memory: '80GB'})
CREATE (e2:Expert {id: 'expert-02', type: 'mlp', memory: '80GB'})
CREATE (r1:Rack {id: 'rack-a'})

CREATE (e1)-[:LOCATED_IN]->(r1)
CREATE (e2)-[:LOCATED_IN]->(r1)

// Query distance
// MATCH (a:Expert)-[:LOCATED_IN]->(r:Rack)<-[:LOCATED_IN]-(b:Expert)
// RETURN a, b, r
