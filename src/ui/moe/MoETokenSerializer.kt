// MoETokenSerializer.kt — Interface / Data Serialization
// Layer: UI / Network — Mobile/JVM to Backend Serialization
//
// Fast serialization of high-dimensional token data using ByteBuffer
// on JVM/Android. Prevents Garbage Collection (GC) pauses by avoiding
// massive object allocations for float arrays during MoE inference requests.

package com.omni.moe.serialization

import java.nio.ByteBuffer
import java.nio.ByteOrder

sealed class SerializationResult<out T, out E> {
    data class Ok<T>(val value: T) : SerializationResult<T, Nothing>()
    data class Err<E>(val error: E) : SerializationResult<Nothing, E>()
}

enum SerializationError {
    EmptyInput,
    BufferOverflow,
    InvalidDimensions
}

/**
 * Packs flat token floats into a highly optimized binary payload.
 * Structure:
 * [MagicBytes: 4] [Version: 1] [Dim: 4] [TokenCount: 4] [FloatData...]
 */
class MoETokenSerializer {
    companion object {
        const val MAGIC_BYTES = 0x4D6F4521 // "MoE!"
        const val VERSION: Byte = 1
        const val HEADER_SIZE = 13 // 4 + 1 + 4 + 4
    }

    /**
     * Serializes a FloatArray into a Direct ByteBuffer.
     */
    fun serialize(tokens: FloatArray, dim: Int): SerializationResult<ByteBuffer, SerializationError> {
        if (tokens.isEmpty()) {
            return SerializationResult.Err(SerializationError.EmptyInput)
        }
        if (tokens.size % dim != 0) {
            return SerializationResult.Err(SerializationError.InvalidDimensions)
        }

        val tokenCount = tokens.size / dim
        val totalBytes = HEADER_SIZE + (tokens.size * 4)

        // Use allocateDirect to avoid JVM GC overhead during network I/O
        val buffer = try {
            ByteBuffer.allocateDirect(totalBytes).order(ByteOrder.LITTLE_ENDIAN)
        } catch (e: OutOfMemoryError) {
            return SerializationResult.Err(SerializationError.BufferOverflow)
        }

        // Write Header
        buffer.putInt(MAGIC_BYTES)
        buffer.put(VERSION)
        buffer.putInt(dim)
        buffer.putInt(tokenCount)

        // Write Data
        val floatBuffer = buffer.asFloatBuffer()
        floatBuffer.put(tokens)
        
        // Reset position for reading
        buffer.position(0)

        return SerializationResult.Ok(buffer)
    }

    /**
     * Deserializes a ByteBuffer back into a FloatArray.
     */
    fun deserialize(buffer: ByteBuffer): SerializationResult<FloatArray, SerializationError> {
        buffer.order(ByteOrder.LITTLE_ENDIAN)
        
        if (buffer.remaining() < HEADER_SIZE) {
            return SerializationResult.Err(SerializationError.EmptyInput)
        }

        val magic = buffer.int
        if (magic != MAGIC_BYTES) {
            return SerializationResult.Err(SerializationError.InvalidDimensions) // Bad magic
        }

        val version = buffer.get()
        val dim = buffer.int
        val tokenCount = buffer.int

        val expectedDataSize = tokenCount * dim * 4
        if (buffer.remaining() < expectedDataSize) {
            return SerializationResult.Err(SerializationError.BufferOverflow)
        }

        val tokens = FloatArray(tokenCount * dim)
        val floatBuffer = buffer.asFloatBuffer()
        floatBuffer.get(tokens)

        return SerializationResult.Ok(tokens)
    }
}
