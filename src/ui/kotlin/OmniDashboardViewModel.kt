// OMNI Domain — Kotlin Compose Multiplatform Model Dashboard
// Cross-platform desktop/mobile model management UI.

package dev.omni.compose.dashboard

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class ModelInfo(
    val id: String,
    val name: String,
    val version: String,
    val status: String,
    val parameters: Long,
    val latencyMs: Double = 0.0,
    val throughputRps: Double = 0.0,
    val gpuUtilization: Double = 0.0
)

data class DashboardState(
    val models: List<ModelInfo> = emptyList(),
    val selectedModel: ModelInfo? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val searchQuery: String = "",
    val sortBy: String = "name"
)

sealed interface DashboardAction {
    data object Refresh : DashboardAction
    data class SelectModel(val model: ModelInfo) : DashboardAction
    data class Search(val query: String) : DashboardAction
    data class Sort(val by: String) : DashboardAction
    data class Deploy(val modelId: String, val env: String) : DashboardAction
}

class DashboardViewModel(private val apiUrl: String = "http://localhost:8080/api/v1") {
    private val _state = MutableStateFlow(DashboardState())
    val state: StateFlow<DashboardState> = _state.asStateFlow()
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    fun dispatch(action: DashboardAction) {
        when (action) {
            is DashboardAction.Refresh -> refresh()
            is DashboardAction.SelectModel -> _state.update { it.copy(selectedModel = action.model) }
            is DashboardAction.Search -> _state.update { it.copy(searchQuery = action.query) }
            is DashboardAction.Sort -> sortModels(action.by)
            is DashboardAction.Deploy -> deployModel(action.modelId, action.env)
        }
    }

    private fun refresh() {
        scope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            try {
                // Production: HTTP call to fetch models
                val models = listOf(
                    ModelInfo("1", "omni-7b", "2.0", "production", 7_000_000_000, 45.2, 120.0, 0.72),
                    ModelInfo("2", "omni-13b", "1.5", "staging", 13_000_000_000, 92.1, 55.0, 0.85),
                    ModelInfo("3", "omni-tiny", "3.0", "production", 500_000_000, 8.3, 450.0, 0.25),
                )
                _state.update { it.copy(models = models, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    private fun sortModels(by: String) {
        _state.update { state ->
            val sorted = when (by) {
                "name" -> state.models.sortedBy { it.name }
                "latency" -> state.models.sortedBy { it.latencyMs }
                "params" -> state.models.sortedByDescending { it.parameters }
                else -> state.models
            }
            state.copy(models = sorted, sortBy = by)
        }
    }

    private fun deployModel(modelId: String, env: String) {
        scope.launch {
            _state.update { it.copy(isLoading = true) }
            // Production: HTTP POST to deploy
            delay(1000)
            _state.update { it.copy(isLoading = false) }
        }
    }

    fun filteredModels(): List<ModelInfo> {
        val s = _state.value
        return if (s.searchQuery.isBlank()) s.models
        else s.models.filter { it.name.contains(s.searchQuery, ignoreCase = true) }
    }

    fun destroy() { scope.cancel() }
}
