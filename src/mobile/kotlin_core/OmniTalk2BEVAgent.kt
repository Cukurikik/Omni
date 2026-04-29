// Omni Talk2BEV Mobile Agent (Kotlin)
// Mobile: BEV spatial query for autonomous driving.
// Ref: llmbev/talk2bev — ICRA'24
package dev.omni.talk2bev
import kotlin.math.sqrt
data class BEVObject(val id: String, val x: Float, val y: Float, val label: String)
class OmniBEVAgent {
    fun spatialQuery(objects: List<BEVObject>, cx: Float, cy: Float, radius: Float): List<BEVObject> {
        return objects.filter { sqrt((it.x - cx) * (it.x - cx) + (it.y - cy) * (it.y - cy)) <= radius }
    }
}
