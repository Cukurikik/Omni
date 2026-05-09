// MoERequestInterceptor.kt — Domain/Interface Layer
// Layer: Interface / API — MoE Gateway Interceptor
//
// Intercepts API requests to the MoE gateway, enforces tenant quotas,
// validates routing hints, and injects request tracing context.
// Strict adherence to monadic error handling (Result type).

package com.omni.moe.gateway.interceptors

import java.util.UUID

sealed class Result<out T, out E> {
    data class Ok<T>(val value: T) : Result<T, Nothing>()
    data class Err<E>(val error: E) : Result<Nothing, E>()
}

data class GatewayRequest(
    val id: String,
    val tenantId: String,
    val payload: String,
    val headers: Map<String, String>
)

data class AuthorizedRequest(
    val originalRequest: GatewayRequest,
    val traceId: String,
    val allowedExperts: List<Int>?,
    val priority: Int
)

sealed class InterceptError {
    data class Unauthorized(val msg: String) : InterceptError()
    data class QuotaExceeded(val tenantId: String, val limit: Int) : InterceptError()
    data class InvalidRoutingHint(val expertId: Int) : InterceptError()
}

interface TenantQuotaService {
    fun checkQuota(tenantId: String): Result<Unit, InterceptError>
}

class MoERequestInterceptor(
    private val quotaService: TenantQuotaService,
    private val globalMaxExperts: Int = 256
) {
    fun intercept(req: GatewayRequest): Result<AuthorizedRequest, InterceptError> {
        // 1. Verify tenant authentication
        if (req.tenantId.isBlank()) {
            return Result.Err(InterceptError.Unauthorized("Missing tenant ID"))
        }

        // 2. Enforce quota
        when (val quotaResult = quotaService.checkQuota(req.tenantId)) {
            is Result.Err -> return quotaResult
            is Result.Ok -> { /* pass */ }
        }

        // 3. Process routing hints if present
        val allowedExperts = parseRoutingHints(req.headers["X-MoE-Route-Hint"])
        when (allowedExperts) {
            is Result.Err -> return allowedExperts
            is Result.Ok -> {
                val traceId = req.headers["X-Trace-Id"] ?: UUID.randomUUID().toString()
                
                // Extract priority
                val priority = req.headers["X-Priority"]?.toIntOrNull() ?: 1

                val authReq = AuthorizedRequest(
                    originalRequest = req,
                    traceId = traceId,
                    allowedExperts = allowedExperts.value,
                    priority = priority
                )
                return Result.Ok(authReq)
            }
        }
    }

    private fun parseRoutingHints(hintStr: String?): Result<List<Int>?, InterceptError> {
        if (hintStr.isNullOrBlank()) {
            return Result.Ok(null)
        }

        val experts = mutableListOf<Int>()
        val parts = hintStr.split(",")
        
        for (part in parts) {
            val id = part.trim().toIntOrNull()
            if (id == null || id < 0 || id >= globalMaxExperts) {
                return Result.Err(InterceptError.InvalidRoutingHint(id ?: -1))
            }
            experts.add(id)
        }
        
        return Result.Ok(experts)
    }
}
