! OMNI Scientific/HPC Layer — Fortran Matrix Operations
! High-performance BLAS-accelerated matrix ops for transformers.

module omni_matrix_ops
    use iso_fortran_env, only: real32, real64, int32, int64
    implicit none
    private
    public :: omni_matmul, omni_softmax, omni_rmsnorm, omni_gelu, omni_silu
    public :: omni_attention_scores, omni_layer_norm

contains

    ! Matrix multiplication using BLAS SGEMM
    subroutine omni_matmul(A, B, C, M, N, K, alpha, beta)
        integer(int32), intent(in) :: M, N, K
        real(real32), intent(in) :: A(M, K), B(K, N)
        real(real32), intent(inout) :: C(M, N)
        real(real32), intent(in), optional :: alpha, beta
        real(real32) :: a_val, b_val

        a_val = 1.0; b_val = 0.0
        if (present(alpha)) a_val = alpha
        if (present(beta)) b_val = beta

        call sgemm('N', 'N', M, N, K, a_val, A, M, B, K, b_val, C, M)
    end subroutine

    ! Softmax over a vector (in-place, numerically stable)
    subroutine omni_softmax(x, n)
        integer(int32), intent(in) :: n
        real(real32), intent(inout) :: x(n)
        real(real32) :: max_val, sum_val
        integer :: i

        max_val = maxval(x)
        do i = 1, n
            x(i) = exp(x(i) - max_val)
        end do
        sum_val = sum(x)
        x = x / sum_val
    end subroutine

    ! RMS Normalization
    subroutine omni_rmsnorm(out, x, weight, n, eps)
        integer(int32), intent(in) :: n
        real(real32), intent(in) :: x(n), weight(n), eps
        real(real32), intent(out) :: out(n)
        real(real32) :: ss
        integer :: i

        ss = 0.0
        do i = 1, n
            ss = ss + x(i) * x(i)
        end do
        ss = 1.0 / sqrt(ss / real(n) + eps)
        do i = 1, n
            out(i) = x(i) * ss * weight(i)
        end do
    end subroutine

    ! Layer Normalization
    subroutine omni_layer_norm(out, x, gamma, beta, n, eps)
        integer(int32), intent(in) :: n
        real(real32), intent(in) :: x(n), gamma(n), beta(n), eps
        real(real32), intent(out) :: out(n)
        real(real32) :: mean_val, var_val, inv_std
        integer :: i

        mean_val = sum(x) / real(n)
        var_val = 0.0
        do i = 1, n
            var_val = var_val + (x(i) - mean_val)**2
        end do
        var_val = var_val / real(n)
        inv_std = 1.0 / sqrt(var_val + eps)
        do i = 1, n
            out(i) = (x(i) - mean_val) * inv_std * gamma(i) + beta(i)
        end do
    end subroutine

    ! GELU activation
    elemental function omni_gelu(x) result(y)
        real(real32), intent(in) :: x
        real(real32) :: y
        y = x * 0.5 * (1.0 + tanh(0.7978845608 * (x + 0.044715 * x**3)))
    end function

    ! SiLU activation
    elemental function omni_silu(x) result(y)
        real(real32), intent(in) :: x
        real(real32) :: y
        y = x / (1.0 + exp(-x))
    end function

    ! Compute attention scores: scores = Q @ K^T / sqrt(d)
    subroutine omni_attention_scores(Q, K, scores, seq_q, seq_k, head_dim, scale)
        integer(int32), intent(in) :: seq_q, seq_k, head_dim
        real(real32), intent(in) :: Q(seq_q, head_dim), K(seq_k, head_dim), scale
        real(real32), intent(out) :: scores(seq_q, seq_k)

        call sgemm('N', 'T', seq_q, seq_k, head_dim, scale, Q, seq_q, K, seq_k, 0.0, scores, seq_q)
    end subroutine

end module omni_matrix_ops
