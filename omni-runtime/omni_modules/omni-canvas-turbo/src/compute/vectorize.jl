# omni-canvas-turbo â€” Julia SIMD Vectorization Engine
module omni_canvas_turboVectorize

export vec_add!, vec_mul!, vec_dot, vec_norm, vec_normalize!, mat_mul!

function vec_add!(dst::Vector{Float64}, a::Vector{Float64}, b::Vector{Float64})
    @inbounds @simd for i in eachindex(a) dst[i] = a[i] + b[i] end
    return dst
end

function vec_mul!(dst::Vector{Float64}, a::Vector{Float64}, scalar::Float64)
    @inbounds @simd for i in eachindex(a) dst[i] = a[i] * scalar end
    return dst
end

function vec_dot(a::Vector{Float64}, b::Vector{Float64})::Float64
    s = 0.0; @inbounds @simd for i in eachindex(a) s += a[i] * b[i] end; return s
end

function vec_norm(a::Vector{Float64})::Float64 return sqrt(vec_dot(a, a)) end

function vec_normalize!(a::Vector{Float64})
    n = vec_norm(a); if n > 0.0 vec_mul!(a, a, 1.0/n) end; return a
end

function mat_mul!(C::Matrix{Float64}, A::Matrix{Float64}, B::Matrix{Float64})
    m, k = size(A); k2, n = size(B)
    @inbounds for j in 1:n for l in 1:k
        bval = B[l,j]; @simd for i in 1:m C[i,j] += A[i,l] * bval end
    end end
    return C
end

end # module