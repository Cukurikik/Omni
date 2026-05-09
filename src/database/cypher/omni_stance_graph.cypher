// OMNI Framework - Cypher queries for Stance Detection KE-MLM Graph
// Merges entities and their calculated stances

MERGE (t:Tweet {id: $tweet_id})
SET t.content = $content, t.timestamp = datetime()

MERGE (e:Entity {name: $entity_name})

MERGE (t)-[s:HAS_STANCE]->(e)
SET s.score = $stance_score, 
    s.label = $stance_label,
    s.confidence = $confidence

RETURN t, s, e
