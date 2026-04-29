// Omni InfiGUI-G1 Mobile Agent (Kotlin)
// Mobile Layer: GUI agent action dispatcher for Android.
// Ref: InfiXAI/InfiGUI-G1 — AAAI 2026 Oral
package dev.omni.infigui
data class GUIAction(val type: String, val x: Float, val y: Float, val elementId: String?)
sealed class ActionResult {
    data class Success(val action: GUIAction, val reward: Float) : ActionResult()
    data class Failure(val reason: String) : ActionResult()
}
class OmniGUIAgent {
    fun dispatch(action: GUIAction): ActionResult {
        if (action.x < 0 || action.y < 0) return ActionResult.Failure("Invalid coordinates")
        if (action.type !in setOf("click", "type", "scroll", "swipe"))
            return ActionResult.Failure("Unknown action type")
        return ActionResult.Success(action, 1.0f)
    }
}
