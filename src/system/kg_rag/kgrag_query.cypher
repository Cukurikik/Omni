// KG-RAG Cypher Query
MATCH (disease:Disease {name: "Multiple Sclerosis"})-[:HAS_SYMPTOM]->(symptom:Symptom)
MATCH (drug:Drug)-[:TREATS]->(disease)
RETURN disease.name, collect(DISTINCT symptom.name) as symptoms, collect(DISTINCT drug.name) as treatments
LIMIT 10;
