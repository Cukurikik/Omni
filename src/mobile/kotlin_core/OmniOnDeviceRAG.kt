// Omni OnDevice-RAG Engine (Kotlin)
package dev.omni.ondevicerag
import kotlin.math.sqrt
data class Chunk(val id: Int, val text: String, val embedding: List<Float>)
class OmniOnDeviceRAG {
    private val chunks = mutableListOf<Chunk>()
    fun addChunk(chunk: Chunk) { chunks.add(chunk) }
    fun retrieve(queryEmb: List<Float>, topK: Int = 5): List<Chunk> {
        return chunks.map { it to cosineSim(queryEmb, it.embedding) }
            .sortedByDescending { it.second }.take(topK).map { it.first }
    }
    private fun cosineSim(a: List<Float>, b: List<Float>): Float {
        val dot = a.zip(b).sumOf { (x, y) -> (x * y).toDouble() }.toFloat()
        val na = sqrt(a.sumOf { (it * it).toDouble() }.toFloat())
        val nb = sqrt(b.sumOf { (it * it).toDouble() }.toFloat())
        return if (na > 0 && nb > 0) dot / (na * nb) else 0f
    }
}
