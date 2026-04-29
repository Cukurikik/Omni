package dev.omni.tflite

import org.tensorflow.lite.Interpreter
import java.nio.ByteBuffer

class TfLiteRunner(private val modelBuffer: ByteBuffer) {
    private var interpreter: Interpreter? = null

    init {
        val options = Interpreter.Options().apply {
            setNumThreads(4)
        }
        interpreter = Interpreter(modelBuffer, options)
    }

    fun runInference(input: FloatArray, output: FloatArray) {
        interpreter?.run(input, output) ?: throw IllegalStateException("Interpreter not initialized")
    }

    fun close() {
        interpreter?.close()
        interpreter = null
    }
}
