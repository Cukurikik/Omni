package dev.omni.llmrank

import androidx.compose.runtime.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

// OMNI Monadic Result
sealed class OmniResult<out T, out E> {
    data class Ok<out T>(val value: T) : OmniResult<T, Nothing>()
    data class Err<out E>(val error: E) : OmniResult<Nothing, E>()
}

class LLMRankAdminController {
    fun updateBradleyTerryWeight(weight: Float): OmniResult<Boolean, String> {
        if (weight < 0.0f || weight > 10.0f) {
            return OmniResult.Err("OMNI_DOMAIN_ERR: Weight must be between 0.0 and 10.0")
        }
        // FFI bridge to Mojo compute layer parameter update
        return OmniResult.Ok(true)
    }
}

@Composable
fun LLMRankAdminPanel() {
    val controller = remember { LLMRankAdminController() }
    var currentWeight by remember { mutableStateOf(1.0f) }
    var statusMessage by remember { mutableStateOf("Ready") }
    
    Column(modifier = Modifier.padding(16.dp)) {
        Text("LLMRank Control Panel", style = MaterialTheme.typography.titleLarge)
        Spacer(modifier = Modifier.height(16.dp))
        
        Text("Bradley-Terry Model Weight: $currentWeight")
        Slider(
            value = currentWeight,
            onValueChange = { currentWeight = it },
            valueRange = 0f..10f,
            onValueChangeFinished = {
                when (val res = controller.updateBradleyTerryWeight(currentWeight)) {
                    is OmniResult.Ok -> statusMessage = "Weight updated successfully."
                    is OmniResult.Err -> statusMessage = res.error
                }
            }
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        Text(statusMessage, color = if (statusMessage.startsWith("OMNI")) androidx.compose.ui.graphics.Color.Red else androidx.compose.ui.graphics.Color.Green)
    }
}
