data class OmniResult<T>(val isOk: Boolean, val value: T?, val error: String?)
class XrayViewerActivity {
    private val maxRes = 2048
    fun displayDiagnosis(imageWidth: Int, imageHeight: Int, findings: List<String>): OmniResult<Map<String, Any>> {
        if (imageWidth > maxRes || imageHeight > maxRes) return OmniResult(false, null, "Image exceeds ${maxRes}px")
        if (findings.isEmpty()) return OmniResult(false, null, "No findings")
        return OmniResult(true, mapOf("width" to imageWidth, "height" to imageHeight, "findings" to findings.size), null)
    }
}
