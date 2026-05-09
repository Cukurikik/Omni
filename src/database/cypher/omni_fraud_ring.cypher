// OMNI Database — Cypher Query for Abuse Detection
// Detects API abuse rings: multiple users sharing identical API keys or IPs

MATCH (u:User)-[:USED_IP]->(ip:IPAddress)<-[:USED_IP]-(other:User)
WHERE u.id <> other.id 
  AND size((ip)<-[:USED_IP]-()) > 5 // IP used by more than 5 distinct users
WITH ip, collect(u.id) as SuspectUsers
MATCH (k:ApiKey)-[:OWNED_BY]->(u:User)
WHERE u.id IN SuspectUsers
RETURN ip.address, SuspectUsers, collect(k.hash) as Keys
ORDER BY size(SuspectUsers) DESC
LIMIT 10
