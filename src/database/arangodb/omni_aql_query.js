// ArangoDB AQL Query via JavaScript Driver
// Graph Traversal for Microservice Dependency Tracing in OMNI
const { db } = require('@arangodb');

function getImpactedServices(failedServiceId) {
    const query = `
        FOR v, e, p IN 1..3 OUTBOUND @startNode GRAPH 'omni_service_graph'
        FILTER e.dependencyType == 'critical'
        RETURN DISTINCT v._id
    `;
    
    const bindVars = { startNode: `Services/${failedServiceId}` };
    const cursor = db._query(query, bindVars);
    
    return cursor.toArray();
}

module.exports = { getImpactedServices };
