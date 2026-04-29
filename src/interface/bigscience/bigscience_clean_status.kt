package dev.omni.bigscience

import androidx.compose.runtime.*
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Text
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

sealed class OmniResult<out T, out E> {
    data class Ok<out T>(val value: T) : OmniResult<T, Nothing>()
    data class Err<out E>(val error: E) : OmniResult<Nothing, E>()
}

data class CleanProgressState(
    val chunksProcessed: Long,
    val duplicatesFound: Long,
    val isComplete: Boolean
)

class BigScienceCleanController {
    fun calculateProgress(processed: Long, total: Long): OmniResult<Float, String> {
        if (total <= 0) return OmniResult.Err("OMNI_ERROR: Total chunks must be > 0")
        if (processed > total) return OmniResult.Err("OMNI_ERROR: Processed cannot exceed total")
        
        return OmniResult.Ok(processed.toFloat() / total.toFloat())
    }
}

@Composable
fun DatasetCleanMonitorView(processed: Long, total: Long, duplicates: Long) {
    val controller = remember { BigScienceCleanController() }
    var progress by remember { mutableStateOf(0f) }
    var errorMsg by remember { mutableStateOf<String?>(null) }
    
    LaunchedEffect(processed, total) {
        when (val res = controller.calculateProgress(processed, total)) {
            is OmniResult.Ok -> progress = res.value
            is OmniResult.Err -> errorMsg = res.error
        }
    }
    
    Column(modifier = Modifier.padding(16.dp)) {
        Text("BigScience LSH Dedup Monitor", style = androidx.compose.material3.MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(16.dp))
        
        if (errorMsg != null) {
            Text(errorMsg!!, color = androidx.compose.ui.graphics.Color.Red)
        } else {
            LinearProgressIndicator(progress = progress, modifier = Modifier.fillMaxWidth())
            Spacer(modifier = Modifier.height(8.dp))
            Text("Progress: ${(progress * 100).toInt()}%")
            Text("Duplicates Removed: $duplicates")
        }
    }
}
