! OMNI MOTHER: Fortran 90 Scientific Computing
! High-performance legacy math backend for load calculations

module omni_pikv_math
    implicit none
contains
    function calculate_cv_squared(loads, n) result(cv2)
        real*8, intent(in) :: loads(n)
        integer, intent(in) :: n
        real*8 :: cv2, mean, var, sum_x, sum_sq
        integer :: i
        
        sum_x = 0.0d0
        do i = 1, n
            sum_x = sum_x + loads(i)
        end do
        mean = sum_x / n
        
        sum_sq = 0.0d0
        do i = 1, n
            sum_sq = sum_sq + (loads(i) - mean)**2
        end do
        var = sum_sq / n
        
        cv2 = var / (mean**2)
    end function calculate_cv_squared
end module omni_pikv_math
