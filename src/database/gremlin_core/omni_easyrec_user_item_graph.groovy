// Omni EasyRec User-Item Graph (Gremlin)
// Database Layer: Recommendation graph traversal.
// Ref: HKUDS/EasyRec — EMNLP 2025
g.V().hasLabel('user').has('user_id', userId)
 .outE('interacted_with')
 .inV().hasLabel('item')
 .outE('similar_to')
 .inV().hasLabel('item')
 .dedup()
 .order().by('embedding_score', Order.desc)
 .limit(20)
 .valueMap('item_id', 'title', 'embedding_score')
 .toList()
