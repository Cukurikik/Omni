// Omni Conversant Persona Mobile (Kotlin)
package dev.omni.conversant
data class Persona(val name: String, val preamble: String, val examples: List<Map<String,String>> = emptyList())
class OmniConversantAgent {
    fun buildContext(persona: Persona, history: List<Map<String,String>>, maxTurns: Int = 10): String {
        val ctx = StringBuilder("Persona: ${persona.preamble}\n\n")
        history.takeLast(maxTurns).forEach { ctx.append("${it["role"]?.capitalize()}: ${it["content"]}\n") }
        return ctx.toString()
    }
    fun conversationQuality(turns: List<Map<String,String>>): Double {
        if (turns.isEmpty()) return 0.0
        val avgLen = turns.map { (it["content"]?.split(" ")?.size ?: 0) }.average()
        return minOf(1.0, avgLen / 50)
    }
}
