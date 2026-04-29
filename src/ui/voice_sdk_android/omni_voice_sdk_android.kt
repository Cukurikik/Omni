package omni.domain.voicesdk

// OMNI Voice SDK Android Domain — Interface/Domain Layer
// Absorbing alan-ai/alan-sdk-android voice command lifecycle management.
// Kotlin-idiomatic sealed Result type for voice intent handling.

sealed class VoiceResult<out T> {
    data class Ok<T>(val value: T) : VoiceResult<T>()
    data class Fail(val error: String) : VoiceResult<Nothing>()
}

data class VoiceCommand(
    val intent: String,
    val confidence: Double,
    val transcript: String,
    val timestamp: Long = System.currentTimeMillis()
)

class OmniVoiceSdkAndroidEngine {
    private val intentRegistry = mutableMapOf<String, (VoiceCommand) -> Any>()
    private var dispatchCount = 0L

    fun registerIntent(intent: String, handler: (VoiceCommand) -> Any): VoiceResult<Boolean> {
        if (intent.isBlank()) return VoiceResult.Fail("VoiceSDKError: Empty intent name")
        intentRegistry[intent] = handler
        return VoiceResult.Ok(true)
    }

    fun processCommand(command: VoiceCommand): VoiceResult<Any> {
        if (command.confidence < 0.3) {
            return VoiceResult.Fail("VoiceSDKError: Confidence too low (${command.confidence})")
        }
        val handler = intentRegistry[command.intent]
            ?: return VoiceResult.Fail("VoiceSDKError: Unknown intent '${command.intent}'")
        dispatchCount++
        return try {
            VoiceResult.Ok(handler(command))
        } catch (e: Exception) {
            VoiceResult.Fail("VoiceSDKError: ${e.message}")
        }
    }

    fun diagnostics(): Map<String, Any> = mapOf(
        "engine" to "OmniVoiceSdkAndroidEngine",
        "intents" to intentRegistry.size,
        "dispatched" to dispatchCount,
        "status" to "Operational"
    )
}
