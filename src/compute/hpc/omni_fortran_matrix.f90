module omni_fortran_matrix
    ! Omni Scientific BLAS Core (Fortran)
    ! Scientific & HPC Layer
    ! Leverages Fortran's strict memory aliasing guarantees to generate 
    ! maximum throughput assembly for dense matrix multiplication.

    implicit none
    private
    public :: sgemm_omni

contains

    subroutine sgemm_omni(m, n, k, alpha, A, B, beta, C)
        integer, intent(in) :: m, n, k
        real, intent(in) :: alpha, beta
        real, intent(in), dimension(m, k) :: A
        real, intent(in), dimension(k, n) :: B
        real, intent(inout), dimension(m, n) :: C
        
        integer :: i, j, l
        
        ! Pre-scale C by beta
        if (beta == 0.0) then
            C = 0.0
        else
            C = beta * C
        end if
        
        ! Perform C = alpha * A * B + C
        ! Optimized loop order for Column-Major data (Fortran standard)
        do j = 1, n
            do l = 1, k
                do i = 1, m
                    C(i, j) = C(i, j) + alpha * A(i, l) * B(l, j)
                end do
            end do
        end do
        
    end subroutine sgemm_omni

end module omni_fortran_matrix
