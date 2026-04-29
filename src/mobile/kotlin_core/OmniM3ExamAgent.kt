// Omni M3Exam Mobile Agent (Kotlin)
// Ref: DAMO-NLP-SG/M3Exam
package dev.omni.m3exam
data class ExamResult(val language: String, val level: String, val accuracy: Double)
class OmniM3ExamAgent {
    fun evaluate(prediction: String, answer: String): Boolean =
        prediction.trim().uppercase() == answer.trim().uppercase()
    fun batchEvaluate(items: List<Pair<String, String>>): Double {
        val correct = items.count { evaluate(it.first, it.second) }
        return correct.toDouble() / items.size.coerceAtLeast(1)
    }
}
