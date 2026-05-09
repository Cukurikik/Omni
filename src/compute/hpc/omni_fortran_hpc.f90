! OMNI Scientific & HPC Layer
! Fortran 90 interface for dense tensor operations executing on legacy supercomputers
! Utilizes highly optimized BLAS/LAPACK routines natively.

module omni_tensor_math
    implicit none

contains

    !> Performs C = alpha*A*B + beta*C (General Matrix Multiplication)
    subroutine omni_gemm(m, n, k, alpha, A, lda, B, ldb, beta, C, ldc)
        integer, intent(in) :: m, n, k, lda, ldb, ldc
        real(8), intent(in) :: alpha, beta
        real(8), intent(in), dimension(lda, *) :: A
        real(8), intent(in), dimension(ldb, *) :: B
        real(8), intent(inout), dimension(ldc, *) :: C

        ! Call to optimized BLAS implementation (e.g., OpenBLAS, MKL)
        call dgemm('N', 'N', m, n, k, alpha, A, lda, B, ldb, beta, C, ldc)
    end subroutine omni_gemm

    !> Computes the Softmax across columns of a matrix
    subroutine omni_softmax(m, n, A, lda)
        integer, intent(in) :: m, n, lda
        real(8), intent(inout), dimension(lda, n) :: A
        integer :: i, j
        real(8) :: max_val, sum_exp

        do j = 1, n
            ! Find max for numerical stability
            max_val = A(1, j)
            do i = 2, m
                if (A(i, j) > max_val) max_val = A(i, j)
            end do

            sum_exp = 0.0d0
            do i = 1, m
                A(i, j) = exp(A(i, j) - max_val)
                sum_exp = sum_exp + A(i, j)
            end do

            ! Normalize
            do i = 1, m
                A(i, j) = A(i, j) / sum_exp
            end do
        end do
    end subroutine omni_softmax

end module omni_tensor_math
