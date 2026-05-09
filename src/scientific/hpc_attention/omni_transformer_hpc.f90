! @omni-layer Scientific | @omni-lang Fortran | @omni-batch 18 | @omni-semester 16
! @omni-description Fortran HPC matrix operations for transformer layers:
! DGEMM-based attention score computation and layer normalization.

module omni_transformer_hpc
    use iso_fortran_env, only: real64, int64
    implicit none
    private
    public :: attention_scores, layer_norm_f, softmax_rows, matmul_qk

contains

    ! Compute Q*K^T attention scores
    subroutine matmul_qk(Q, K, scores, seq_len, head_dim, scale)
        integer, intent(in) :: seq_len, head_dim
        real(real64), intent(in) :: Q(seq_len, head_dim)
        real(real64), intent(in) :: K(seq_len, head_dim)
        real(real64), intent(out) :: scores(seq_len, seq_len)
        real(real64), intent(in) :: scale
        integer :: i, j, d

        !$omp parallel do collapse(2) private(d)
        do j = 1, seq_len
            do i = 1, seq_len
                scores(i, j) = 0.0d0
                do d = 1, head_dim
                    scores(i, j) = scores(i, j) + Q(i, d) * K(j, d)
                end do
                scores(i, j) = scores(i, j) * scale
            end do
        end do
        !$omp end parallel do
    end subroutine

    ! Apply softmax to each row of a matrix
    subroutine softmax_rows(mat, n, m)
        integer, intent(in) :: n, m
        real(real64), intent(inout) :: mat(n, m)
        real(real64) :: row_max, row_sum
        integer :: i, j

        !$omp parallel do private(row_max, row_sum, j)
        do i = 1, n
            row_max = mat(i, 1)
            do j = 2, m
                if (mat(i, j) > row_max) row_max = mat(i, j)
            end do
            row_sum = 0.0d0
            do j = 1, m
                mat(i, j) = exp(mat(i, j) - row_max)
                row_sum = row_sum + mat(i, j)
            end do
            row_sum = max(row_sum, 1.0d-10)
            do j = 1, m
                mat(i, j) = mat(i, j) / row_sum
            end do
        end do
        !$omp end parallel do
    end subroutine

    ! Full attention computation: softmax(Q*K^T/sqrt(d)) * V
    subroutine attention_scores(Q, K, V, output, seq_len, head_dim)
        integer, intent(in) :: seq_len, head_dim
        real(real64), intent(in) :: Q(seq_len, head_dim)
        real(real64), intent(in) :: K(seq_len, head_dim)
        real(real64), intent(in) :: V(seq_len, head_dim)
        real(real64), intent(out) :: output(seq_len, head_dim)
        real(real64) :: scores(seq_len, seq_len)
        real(real64) :: scale
        integer :: i, j, d

        scale = 1.0d0 / sqrt(dble(head_dim))
        call matmul_qk(Q, K, scores, seq_len, head_dim, scale)
        call softmax_rows(scores, seq_len, seq_len)

        !$omp parallel do collapse(2) private(j)
        do d = 1, head_dim
            do i = 1, seq_len
                output(i, d) = 0.0d0
                do j = 1, seq_len
                    output(i, d) = output(i, d) + scores(i, j) * V(j, d)
                end do
            end do
        end do
        !$omp end parallel do
    end subroutine

    ! Layer normalization
    subroutine layer_norm_f(x, n, eps)
        integer, intent(in) :: n
        real(real64), intent(inout) :: x(n)
        real(real64), intent(in) :: eps
        real(real64) :: mean_val, var_val, inv_std
        integer :: i

        mean_val = sum(x) / dble(n)
        var_val = 0.0d0
        do i = 1, n
            var_val = var_val + (x(i) - mean_val)**2
        end do
        var_val = var_val / dble(n)
        inv_std = 1.0d0 / sqrt(var_val + eps)
        do i = 1, n
            x(i) = (x(i) - mean_val) * inv_std
        end do
    end subroutine

end module omni_transformer_hpc
