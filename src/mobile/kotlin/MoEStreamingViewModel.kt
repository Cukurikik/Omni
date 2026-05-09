package dev.omni.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.omni.mobile.client.OmniMoEAndroidClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch

/**
 * OMNI Framework - MoE Streaming ViewModel (Kotlin/Android)
 * Manages the UI state for the Android application while receiving 
 * Server-Sent Events (SSE) from the MoE inference client.
 */
class MoEStreamingViewModel(private val apiClient: OmniMoEAndroidClient) : ViewModel() {

    private val _generatedText = MutableStateFlow("")
    val generatedText: StateFlow<String> = _generatedText

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    fun generateResponse(prompt: String) {
        _generatedText.value = ""
        _isLoading.value = true

        viewModelScope.launch {
            apiClient.streamInference(prompt, maxTokens = 512)
                .catch { e ->
                    _generatedText.value = "Error: ${e.message}"
                    _isLoading.value = false
                }
                .collect { chunk ->
                    // Append stream chunk to the UI state
                    _generatedText.value += chunk
                }
            _isLoading.value = false
        }
    }
}
