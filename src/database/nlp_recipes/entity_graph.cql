// NLP Recipes Entity Graph Database
CREATE (org:Organization {name: 'Omni Framework'})
CREATE (loc:Location {name: 'Global Node'})
CREATE (per:Person {name: 'Antigravity Mother'})

CREATE (per)-[:WORKS_FOR]->(org)
CREATE (org)-[:LOCATED_IN]->(loc)

MATCH (p:Person)-[r:WORKS_FOR]->(o:Organization)
RETURN p.name, o.name
