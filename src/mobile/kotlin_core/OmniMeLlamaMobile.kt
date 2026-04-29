// Omni Me-LLaMA Mobile (Kotlin)
// Mobile Layer: Medical entity display for Android inference.
// Ref: BIDS-Xu-Lab/Me-LLaMA

package dev.omni.mellama

sealed class MedicalResult {
    data class Success(val entities: List<String>, val count: Int) : MedicalResult()
    data class Failure(val error: String) : MedicalResult()
}

class OmniMeLlamaEvaluator {
    fun extractEntities(tokens: List<String>, labels: List<String>): MedicalResult {
        if (tokens.size != labels.size) return MedicalResult.Failure("Size mismatch")
        val entities = mutableListOf<String>()
        var i = 0
        while (i < tokens.size) {
            if (labels[i].startsWith("B-")) {
                val sb = StringBuilder(tokens[i])
                i++
                while (i < tokens.size && labels[i].startsWith("I-")) { sb.append(" ").append(tokens[i]); i++ }
                entities.add(sb.toString())
            } else i++
        }
        return MedicalResult.Success(entities, entities.size)
    }
}
