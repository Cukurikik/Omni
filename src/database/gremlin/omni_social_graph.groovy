// OMNI Graph Database Queries using Gremlin
// Maps User to Agent relationships for personalized knowledge graphs

g.addV('User').property('id', 'u1').property('name', 'Alice').as('a')
 .addV('Agent').property('id', 'ag1').property('model', 'omni-gpt-4').as('b')
 .addE('OWNS').from('a').to('b')
 .property('created_at', '2026-05-01')
 .iterate()

// Query: Find all models owned by Alice that were created after 2026-01-01
def models = g.V().has('User', 'name', 'Alice')
              .outE('OWNS').has('created_at', gt('2026-01-01'))
              .inV().values('model').toList()

// Collaborative filtering: Find other users who use the same model
def peers = g.V().has('User', 'name', 'Alice')
             .out('OWNS')
             .in('OWNS')
             .where(neq('a'))
             .values('name').dedup().toList()

println "Alice's models: " + models
println "Peers using the same models: " + peers
