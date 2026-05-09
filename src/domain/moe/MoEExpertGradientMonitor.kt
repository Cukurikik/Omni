// MoEExpertGradientMonitor.kt — Expert Gradient Analysis for MoE Training
// Layer: Domain / Analytics — MoE Training Diagnostics (Kotlin/JVM)
//
// Monitors gradient flow through MoE experts during training to detect:
// - Gradient vanishing in underused experts
// - Gradient explosion in overloaded experts
// - Router gradient saturation
// - Expert divergence patterns

package omni.domain.moe

import kotlin.math.abs
import kotlin.math.sqrt
import kotlin.math.ln

data class GradientStats(
    val expertId: Int,
    val meanGradNorm: Double,
    val maxGradNorm: Double,
    val minGradNorm: Double,
    val gradVariance: Double,
    val isVanishing: Boolean,
    val isExploding: Boolean,
    val updateCount: Long
)

data class RouterGradientStats(
    val meanNorm: Double,
    val saturationRatio: Double,
    val entropyGradient: Double
)

class ExpertGradientAccumulator(private val expertId: Int) {
    private val gradNorms = mutableListOf<Double>()
    private var updateCount: Long = 0

    fun record(gradNorm: Double) {
        gradNorms.add(gradNorm)
        updateCount++
        // Keep rolling window of 1000 for memory efficiency
        if (gradNorms.size > 1000) {
            gradNorms.removeAt(0)
        }
    }

    fun stats(): GradientStats {
        if (gradNorms.isEmpty()) {
            return GradientStats(expertId, 0.0, 0.0, 0.0, 0.0,
                isVanishing = true, isExploding = false, updateCount = 0)
        }
        val mean = gradNorms.average()
        val max = gradNorms.max()
        val min = gradNorms.min()
        val variance = gradNorms.map { (it - mean) * (it - mean) }.average()

        return GradientStats(
            expertId = expertId,
            meanGradNorm = mean,
            maxGradNorm = max,
            minGradNorm = min,
            gradVariance = variance,
            isVanishing = mean < 1e-7,
            isExploding = max > 1e3,
            updateCount = updateCount
        )
    }

    fun reset() {
        gradNorms.clear()
        updateCount = 0
    }
}

class MoEGradientMonitor(private val numExperts: Int) {
    private val expertAccumulators = (0 until numExperts).map {
        ExpertGradientAccumulator(it)
    }
    private val routerNorms = mutableListOf<Double>()
    private var stepCount: Long = 0

    fun recordExpertGradient(expertId: Int, gradNorm: Double) {
        require(expertId in 0 until numExperts) {
            "Expert ID $expertId out of range [0, $numExperts)"
        }
        expertAccumulators[expertId].record(gradNorm)
    }

    fun recordRouterGradient(gradNorm: Double) {
        routerNorms.add(gradNorm)
        if (routerNorms.size > 1000) routerNorms.removeAt(0)
    }

    fun step() {
        stepCount++
    }

    fun expertStats(): List<GradientStats> {
        return expertAccumulators.map { it.stats() }
    }

    fun routerStats(): RouterGradientStats {
        if (routerNorms.isEmpty()) {
            return RouterGradientStats(0.0, 0.0, 0.0)
        }
        val meanNorm = routerNorms.average()
        val saturated = routerNorms.count { it < 1e-6 }
        val satRatio = saturated.toDouble() / routerNorms.size
        return RouterGradientStats(
            meanNorm = meanNorm,
            saturationRatio = satRatio,
            entropyGradient = meanNorm * (1.0 - satRatio)
        )
    }

    fun detectAnomalies(): List<String> {
        val anomalies = mutableListOf<String>()
        val stats = expertStats()

        // Check for gradient vanishing
        val vanishing = stats.filter { it.isVanishing }
        if (vanishing.isNotEmpty()) {
            anomalies.add("GRADIENT_VANISHING: Experts ${vanishing.map { it.expertId }}")
        }

        // Check for gradient explosion
        val exploding = stats.filter { it.isExploding }
        if (exploding.isNotEmpty()) {
            anomalies.add("GRADIENT_EXPLOSION: Experts ${exploding.map { it.expertId }}")
        }

        // Check for expert divergence (high variance across experts)
        val means = stats.map { it.meanGradNorm }
        if (means.isNotEmpty()) {
            val globalMean = means.average()
            val globalStd = sqrt(means.map { (it - globalMean) * (it - globalMean) }.average())
            val cv = globalStd / (globalMean + 1e-8)
            if (cv > 2.0) {
                anomalies.add("EXPERT_DIVERGENCE: CV=${"%.3f".format(cv)}, high gradient variance across experts")
            }
        }

        // Check router saturation
        val rStats = routerStats()
        if (rStats.saturationRatio > 0.5) {
            anomalies.add("ROUTER_SATURATED: ${"%.1f".format(rStats.saturationRatio * 100)}% of gradients near zero")
        }

        return anomalies
    }

    fun summary(): Map<String, Any> {
        val stats = expertStats()
        return mapOf(
            "step" to stepCount,
            "num_experts" to numExperts,
            "expert_stats" to stats.map { mapOf(
                "id" to it.expertId,
                "mean_grad" to "%.6f".format(it.meanGradNorm),
                "vanishing" to it.isVanishing,
                "exploding" to it.isExploding
            )},
            "router" to routerStats(),
            "anomalies" to detectAnomalies()
        )
    }
}
