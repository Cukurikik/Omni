MATCH (u:User)-[:SUBMITTED]->(i:Instruction)-[:BELONGS_TO]->(d:Domain {name: 'Medical'})
WHERE i.quality_score > 0.95
RETURN u.id, i.prompt, i.completion;
