// Omni ROSGPT Mobile Agent (Kotlin)
// Ref: bilel-bj/ROSGPT_Vision
package dev.omni.rosgpt
data class RobotCommand(val type: String, val linearVel: Float, val angularVel: Float)
class OmniROSGPTAgent {
    fun parseCommand(nl: String): RobotCommand {
        val lower = nl.lowercase()
        return when {
            "forward" in lower || "go" in lower -> RobotCommand("move_forward", 0.3f, 0f)
            "left" in lower -> RobotCommand("turn_left", 0f, 0.5f)
            "right" in lower -> RobotCommand("turn_right", 0f, -0.5f)
            "stop" in lower -> RobotCommand("stop", 0f, 0f)
            else -> RobotCommand("unknown", 0f, 0f)
        }
    }
}
