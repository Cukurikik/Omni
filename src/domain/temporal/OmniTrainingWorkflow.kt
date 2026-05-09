// OMNI Business Layer — Temporal SDK Model Training Workflow
// Durable workflow orchestration for long-running ML training.

package omni.workflow

import io.temporal.workflow.*
import io.temporal.activity.*
import java.time.Duration

// Activity interface
@ActivityInterface
interface ModelTrainingActivities {
    fun validateDataset(datasetId: String): DatasetValidationResult
    fun prepareTrainingConfig(modelId: String, hyperparams: Map<String, Any>): TrainingConfig
    fun trainModel(config: TrainingConfig): TrainingResult
    fun evaluateModel(modelId: String, evalDatasetId: String): EvaluationResult
    fun deployModel(modelId: String, environment: String): DeploymentResult
    fun notifyCompletion(result: WorkflowSummary): Boolean
}

data class DatasetValidationResult(val valid: Boolean, val numExamples: Long, val errors: List<String>)
data class TrainingConfig(val modelId: String, val datasetId: String, val epochs: Int, val lr: Double, val batchSize: Int)
data class TrainingResult(val modelId: String, val loss: Double, val checkpointPath: String, val durationMinutes: Long)
data class EvaluationResult(val accuracy: Double, val f1: Double, val perplexity: Double, val passed: Boolean)
data class DeploymentResult(val endpoint: String, val version: String, val replicas: Int, val success: Boolean)
data class WorkflowSummary(val modelId: String, val status: String, val training: TrainingResult?, val evaluation: EvaluationResult?, val deployment: DeploymentResult?)

// Workflow interface
@WorkflowInterface
interface ModelTrainingWorkflow {
    @WorkflowMethod
    fun trainAndDeploy(modelId: String, datasetId: String, hyperparams: Map<String, Any>): WorkflowSummary
}

class ModelTrainingWorkflowImpl : ModelTrainingWorkflow {
    private val activities = Workflow.newActivityStub(
        ModelTrainingActivities::class.java,
        ActivityOptions.newBuilder()
            .setStartToCloseTimeout(Duration.ofHours(24))
            .setHeartbeatTimeout(Duration.ofMinutes(5))
            .setRetryOptions(
                RetryOptions.newBuilder()
                    .setMaximumAttempts(3)
                    .setInitialInterval(Duration.ofSeconds(10))
                    .setBackoffCoefficient(2.0)
                    .build()
            )
            .build()
    )

    override fun trainAndDeploy(modelId: String, datasetId: String, hyperparams: Map<String, Any>): WorkflowSummary {
        // Step 1: Validate dataset
        val validation = activities.validateDataset(datasetId)
        if (!validation.valid) {
            return WorkflowSummary(modelId, "FAILED_VALIDATION", null, null, null)
        }

        // Step 2: Prepare config
        val config = activities.prepareTrainingConfig(modelId, hyperparams)

        // Step 3: Train
        val trainingResult = activities.trainModel(config)

        // Step 4: Evaluate
        val evalResult = activities.evaluateModel(modelId, datasetId)
        if (!evalResult.passed) {
            val summary = WorkflowSummary(modelId, "FAILED_EVALUATION", trainingResult, evalResult, null)
            activities.notifyCompletion(summary)
            return summary
        }

        // Step 5: Deploy
        val deployResult = activities.deployModel(modelId, "production")

        val summary = WorkflowSummary(
            modelId,
            if (deployResult.success) "DEPLOYED" else "DEPLOY_FAILED",
            trainingResult, evalResult, deployResult
        )
        activities.notifyCompletion(summary)
        return summary
    }
}
