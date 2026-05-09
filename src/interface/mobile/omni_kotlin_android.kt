package com.omni.runtime.android

import android.util.Log

/**
 * Omni Android JNI Interface (Kotlin)
 * Interface Layer
 * Binds the Omni Universal Binary to the Android OS through the 
 * Java Native Interface (JNI). Ensures zero-copy buffer passing from JVM to Rust/C++.
 */

class OmniNativeRuntime {

    companion object {
        init {
            // Load the Omni LLVM-compiled shared library (.so)
            System.loadLibrary("omni_universal_binary")
        }
        private const val TAG = "OmniNativeRuntime"
    }

    // Native handles
    private var modelHandle: Long = 0

    /**
     * Loads an Omni-compatible model directly from a file descriptor to bypass JVM memory limits.
     */
    external fun loadModelFd(fd: Int, offset: Long, length: Long): Long

    /**
     * Executes a forward pass using direct ByteBuffer to prevent memory copying.
     * @param inputBuffer Memory-mapped input tensor (e.g., tokens)
     * @param outputBuffer Memory-mapped output tensor
     */
    external fun executeInference(handle: Long, inputBuffer: java.nio.ByteBuffer, outputBuffer: java.nio.ByteBuffer): Int

    /**
     * Releases native memory.
     */
    external fun destroyModel(handle: Long)

    fun initialize(fd: Int, offset: Long, length: Long) {
        if (modelHandle != 0L) {
            Log.w(TAG, "Model already initialized. Overwriting handle.")
            destroyModel(modelHandle)
        }
        modelHandle = loadModelFd(fd, offset, length)
        Log.i(TAG, "Omni Model loaded with native handle: $modelHandle")
    }

    fun infer(input: java.nio.ByteBuffer, output: java.nio.ByteBuffer): Boolean {
        if (modelHandle == 0L) {
            Log.e(TAG, "Cannot infer: Model handle is null")
            return false
        }
        val statusCode = executeInference(modelHandle, input, output)
        return statusCode == 0
    }

    fun cleanup() {
        if (modelHandle != 0L) {
            destroyModel(modelHandle)
            modelHandle = 0L
        }
    }
}
