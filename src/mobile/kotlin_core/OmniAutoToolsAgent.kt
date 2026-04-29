// Omni AutoTools Mobile Agent (Kotlin)
package dev.omni.autotools
data class ToolDef(val name: String, val description: String)
data class ToolResult(val tool: String, val score: Double)
class OmniAutoToolsAgent {
    private val tools = mutableListOf<ToolDef>()
    fun register(tool: ToolDef) { tools.add(tool) }
    fun discover(query: String, topK: Int = 5): List<ToolResult> {
        val qt = query.lowercase().split(" ").toSet()
        return tools.map { t -> ToolResult(t.name, qt.intersect(t.description.lowercase().split(" ").toSet()).size.toDouble() / qt.size.coerceAtLeast(1)) }
            .sortedByDescending { it.score }.take(topK)
    }
}
