package com.omni.mobile

/**
 * OMNI MOTHER: OkHttp Interceptor Mock (Production Grade)
 * Appends Bearer token to all outgoing requests safely.
 */
class AuthInterceptor(private val sessionManager: SessionManager) {

    // Simulating OkHttp Interceptor interface
    fun intercept(requestBuilder: MutableMap<String, String>): MutableMap<String, String> {
        val token = sessionManager.getToken()
        if (token != null) {
            requestBuilder["Authorization"] = "Bearer $token"
        }
        return requestBuilder
    }
}
