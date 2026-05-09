// OMNI Database — Gremlin Knowledge Graph Traversal
// Deep multi-hop traversal to find reasoning chains for LLM grounding

// Find the path from "Artificial Intelligence" to specific implementations
// Traverses through 'includes', 'implementedBy', and 'dependsOn' edges

def findImplementationChains(g, startConcept) {
    return g.V().has('Concept', 'name', startConcept)
            .repeat(out('includes', 'implementedBy', 'dependsOn'))
            .until(hasLabel('Implementation'))
            .path()
            .by('name')
            .limit(10)
            .toList()
}

// Example Execution
// def results = findImplementationChains(g, 'Artificial Intelligence')
// results.each { println it }
