! OMNI Framework - Fortran LAPACK Bindings for Inverse DALL-E OCR
! Performs rapid matrix inversion for optical feature extraction

module omni_dalle_ocr_lapack
    implicit none

contains

    subroutine invert_feature_matrix(matrix, n, info)
        integer, intent(in) :: n
        real*8, dimension(n, n), intent(inout) :: matrix
        integer, intent(out) :: info
        
        integer, dimension(n) :: ipiv
        real*8, dimension(n) :: work
        integer :: lwork
        
        lwork = n
        
        ! Call LAPACK DGETRF for LU decomposition
        call dgetrf(n, n, matrix, n, ipiv, info)
        if (info /= 0) return
        
        ! Call LAPACK DGETRI for matrix inversion
        call dgetri(n, matrix, n, ipiv, work, lwork, info)
    end subroutine invert_feature_matrix

end module omni_dalle_ocr_lapack
