! Omni InstructRAG Vector Norm (Fortran)
! Scientific Layer: High-performance vector normalization.
! Ref: weizhepei/InstructRAG — ICLR 2025
module omni_instructrag_vecnorm
  implicit none
contains
  function vec_l2_norm(v, n) result(norm)
    integer, intent(in) :: n
    real(8), intent(in) :: v(n)
    real(8) :: norm, s
    integer :: i
    s = 0.0d0
    do i = 1, n
      s = s + v(i) * v(i)
    end do
    norm = sqrt(s)
  end function
end module
