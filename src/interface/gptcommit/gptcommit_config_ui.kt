// OMNI Interface Layer: gptcommit_config_ui.kt
// Kotlin Desktop configuration UI for GPTCommit preferences.
// Bound: Max 10 custom prompt templates.

package nexus.omni.semester14.batch6.interface_layer

const val MAX_PROMPT_TEMPLATES = 10

class GptCommitError(val code: Int, val message: String)

class GptCommitResult<T>(val data: T?, val error: GptCommitError?)

class GptCommitConfigViewModel {
    private val templates = mutableListOf<String>()

    fun addTemplate(template: String): GptCommitResult<Boolean> {
        if (templates.size >= MAX_PROMPT_TEMPLATES) {
            return GptCommitResult(null, GptCommitError(1, "Exceeded 10 custom prompt templates limit."))
        }
        
        templates.add(template)
        return GptCommitResult(true, null)
    }

    fun getTemplates(): List<String> {
        return templates.toList()
    }
}
