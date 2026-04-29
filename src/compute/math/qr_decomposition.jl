module OmniMath

using LinearAlgebra

function compute_qr(A::Matrix{Float64})
    # Native Julia QR decomposition
    F = qr(A)
    return F.Q, F.R
end

end
