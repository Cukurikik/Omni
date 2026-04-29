package dev.omniframework.drivelm
class OmniResult<T, E>(val isOk: Boolean, val value: T?, val error: E?)
class DriveLMAnnotator {
    private val maxAnnotations = 10000
    fun addAnnotation(frameId: Int, question: String): OmniResult<Boolean, String> {
        if (question.length > 2048) return OmniResult(false, null, "Question exceeds 2KB")
        if (frameId < 0) return OmniResult(false, null, "Invalid frame ID")
        return OmniResult(true, true, null)
    }
}
