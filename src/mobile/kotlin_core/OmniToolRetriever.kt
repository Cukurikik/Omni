// Omni Tool Retrieval K2 Mobile (Kotlin)
// Ref: mangopy/tool-retrieval-benchmark — Apache-2.0
package dev.omni.toolretrieval
data class ToolDef(val name: String, val description: String)
data class RetrievedTool(val name: String, val score: Double)

class OmniToolRetriever {
    private val tools = mutableListOf<ToolDef>()
    fun register(tool: ToolDef) { tools.add(tool) }
    fun retrieve(query: String, topK: Int = 5): List<RetrievedTool> {
        val qTokens = query.lowercase().split(" ").toSet()
        return tools.map { tool ->
            val descTokens = (tool.description.lowercase() + " " + tool.name.lowercase()).split(" ").toSet()
            val overlap = qTokens.intersect(descTokens).size
            RetrievedTool(tool.name, overlap.toDouble() / qTokens.size.coerceAtLeast(1))
        }.sortedByDescending { it.score }.take(topK)
    }
}
