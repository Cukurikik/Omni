package com.omni.mobile

import java.util.concurrent.atomic.AtomicReference

/**
 * OMNI MOTHER: Android/Kotlin Session Manager (Production Grade)
 * Thread-safe JWT session state holder for mobile platforms.
 */
class SessionManager {
    private val currentToken = AtomicReference<String?>(null)

    fun saveToken(token: String) {
        require(token.isNotBlank()) { "Token cannot be blank" }
        currentToken.set(token)
        println("[OMNI KOTLIN] Session token safely stored.")
    }

    fun getToken(): String? {
        return currentToken.get()
    }

    fun clearSession() {
        currentToken.set(null)
        println("[OMNI KOTLIN] Session terminated.")
    }

    val isLoggedIn: Boolean
        get() = currentToken.get() != null
}
