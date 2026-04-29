// Omni AutoMix Mobile Agent (Kotlin)
// Ref: automix-llm/automix
package dev.omni.automix
data class RouteResult(val model: String, val svScore: Float, val cost: Float)
class OmniAutoMixAgent(private val threshold: Float = 0.6f) {
    fun route(svScore: Float, costSmall: Float, costLarge: Float): RouteResult {
        val model = if (svScore >= threshold) "small" else "large"
        val cost = if (model == "small") costSmall else costLarge
        return RouteResult(model, svScore, cost)
    }
}
