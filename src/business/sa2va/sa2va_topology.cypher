// Sa2VA pixel topology graph
// Cypher for analyzing segmentation associations

// Bound: Limit graph depth traversal to 3 levels
MATCH (px:Pixel)-[:ADJACENT*1..3]->(neighbor:Pixel)
WHERE px.segment_id = neighbor.segment_id
RETURN count(neighbor) as area
LIMIT 1;
