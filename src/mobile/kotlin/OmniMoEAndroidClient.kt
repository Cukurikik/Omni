package dev.omni.mobile.client

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import okhttp3.OkHttpClient
import okhttp3.Request
import okio.IOException
import org.json.JSONObject

/**
 * OMNI Framework - MoE Android Client (Kotlin)
 * Connects to the vLLM/SGLang backend and processes Server-Sent Events (SSE)
 * to stream generated text chunk by chunk to the Android UI.
 */
class OmniMoEAndroidClient(private val serverUrl: String) {

    private val client = OkHttpClient()

    fun streamInference(prompt: String, maxTokens: Int): Flow<String> = flow {
        println("OMNI Kotlin: Initiating streaming connection to $serverUrl")
        
        // Construct the payload
        val jsonPayload = JSONObject().apply {
            put("prompt", prompt)
            put("max_tokens", maxTokens)
            put("stream", true)
        }.toString()

        val requestBody = okhttp3.RequestBody.create(
            okhttp3.MediaType.parse("application/json"), jsonPayload
        )

        val request = Request.Builder()
            .url("$serverUrl/v1/generate")
            .post(requestBody)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response")

            val source = response.body()?.source()
            source?.let {
                while (!it.exhausted()) {
                    val line = it.readUtf8Line()
                    if (line != null && line.startsWith("data: ")) {
                        val data = line.substring(6)
                        if (data == "[DONE]") break
                        
                        try {
                            val json = JSONObject(data)
                            val textChunk = json.optString("text", "")
                            emit(textChunk)
                        } catch (e: Exception) {
                            println("OMNI Kotlin Warning: JSON parse error on stream chunk")
                        }
                    }
                }
            }
        }
    }.flowOn(Dispatchers.IO)
}
