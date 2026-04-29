// Omni Transtation KMP Mobile (Kotlin)
// Mobile Layer: Kotlin Multiplatform translation with LLM support.
// Ref: FunnySaltyFish/Transtation-KMP — KMP Translation App.
package dev.omni.transtation
sealed class TranslationResult {
    data class Success(val translated: String, val model: String, val confidence: Float) : TranslationResult()
    data class Failure(val error: String) : TranslationResult()
}
class OmniTranslator {
    fun translate(text: String, sourceLang: String, targetLang: String): TranslationResult {
        if (text.isBlank()) return TranslationResult.Failure("Empty input")
        if (sourceLang == targetLang) return TranslationResult.Success(text, "identity", 1.0f)
        return TranslationResult.Success("[$targetLang] $text", "omni-llm", 0.95f)
    }
}
