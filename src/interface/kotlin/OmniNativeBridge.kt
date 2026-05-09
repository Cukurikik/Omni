package com.omni.framework.bridge

import android.util.Log
import org.json.JSONObject

class OmniNativeBridge {
    
    companion object {
        const val TAG = "OmniNativeBridge"
    }

    init {
        try {
            System.loadLibrary("omni_core_jni")
            Log.i(TAG, "OMNI Core C++ Library loaded successfully.")
        } catch (e: UnsatisfiedLinkError) {
            Log.e(TAG, "Failed to load OMNI Core library", e)
        }
    }

    external fun executeInference(modelPath: String, inputTensor: FloatArray): FloatArray

    fun processPayload(jsonPayload: String): String {
        return try {
            val req = JSONObject(jsonPayload)
            val modelId = req.getString("model_id")
            val data = req.getJSONArray("data")
            
            val floatArray = FloatArray(data.length())
            for (i in 0 until data.length()) {
                floatArray[i] = data.getDouble(i).toFloat()
            }
            
            val result = executeInference(modelId, floatArray)
            val resObj = JSONObject()
            resObj.put("status", "success")
            resObj.put("output", result.contentToString())
            resObj.toString()
            
        } catch (e: Exception) {
            Log.e(TAG, "Payload processing error", e)
            "{\"status\":\"error\",\"message\":\"${e.message}\"}"
        }
    }
}
