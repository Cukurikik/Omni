! @omni-layer Scientific | @omni-lang Fortran 2018 | @omni-batch 17
! @omni-description HPC matrix kernel: Fortran BLAS-style dense matrix
! operations with OpenMP parallelism for scientific computing.

module omni_hpc_matrix
  implicit none
  private
  public :: omni_dgemm, omni_dsymv, omni_dnorm2, omni_dscal
  public :: omni_frobenius_norm, omni_trace, omni_det_3x3

contains

  ! Dense General Matrix Multiply: C = alpha*A*B + beta*C
  subroutine omni_dgemm(A, B, C, M, N, K, alpha, beta)
    integer, intent(in) :: M, N, K
    double precision, intent(in) :: A(M,K), B(K,N), alpha, beta
    double precision, intent(inout) :: C(M,N)
    integer :: i, j, l
    double precision :: temp

    !$OMP PARALLEL DO PRIVATE(i, j, l, temp) SCHEDULE(dynamic)
    do j = 1, N
      do i = 1, M
        temp = 0.0d0
        do l = 1, K
          temp = temp + A(i,l) * B(l,j)
        end do
        C(i,j) = alpha * temp + beta * C(i,j)
      end do
    end do
    !$OMP END PARALLEL DO
  end subroutine omni_dgemm

  ! Symmetric Matrix-Vector Multiply: y = alpha*A*x + beta*y
  subroutine omni_dsymv(A, x, y, N, alpha, beta)
    integer, intent(in) :: N
    double precision, intent(in) :: A(N,N), x(N), alpha, beta
    double precision, intent(inout) :: y(N)
    integer :: i, j
    double precision :: temp

    !$OMP PARALLEL DO PRIVATE(i, j, temp)
    do i = 1, N
      temp = 0.0d0
      do j = 1, N
        temp = temp + A(i,j) * x(j)
      end do
      y(i) = alpha * temp + beta * y(i)
    end do
    !$OMP END PARALLEL DO
  end subroutine omni_dsymv

  ! L2 norm of a vector
  double precision function omni_dnorm2(x, N)
    integer, intent(in) :: N
    double precision, intent(in) :: x(N)
    integer :: i
    double precision :: sum_sq

    sum_sq = 0.0d0
    !$OMP PARALLEL DO REDUCTION(+:sum_sq)
    do i = 1, N
      sum_sq = sum_sq + x(i) * x(i)
    end do
    !$OMP END PARALLEL DO
    omni_dnorm2 = sqrt(sum_sq)
  end function omni_dnorm2

  ! Scale vector: x = alpha * x
  subroutine omni_dscal(x, N, alpha)
    integer, intent(in) :: N
    double precision, intent(inout) :: x(N)
    double precision, intent(in) :: alpha
    integer :: i

    !$OMP PARALLEL DO
    do i = 1, N
      x(i) = alpha * x(i)
    end do
    !$OMP END PARALLEL DO
  end subroutine omni_dscal

  ! Frobenius norm of a matrix
  double precision function omni_frobenius_norm(A, M, N)
    integer, intent(in) :: M, N
    double precision, intent(in) :: A(M,N)
    integer :: i, j
    double precision :: sum_sq

    sum_sq = 0.0d0
    !$OMP PARALLEL DO REDUCTION(+:sum_sq) PRIVATE(i, j)
    do j = 1, N
      do i = 1, M
        sum_sq = sum_sq + A(i,j) * A(i,j)
      end do
    end do
    !$OMP END PARALLEL DO
    omni_frobenius_norm = sqrt(sum_sq)
  end function omni_frobenius_norm

  ! Matrix trace
  double precision function omni_trace(A, N)
    integer, intent(in) :: N
    double precision, intent(in) :: A(N,N)
    integer :: i
    omni_trace = 0.0d0
    do i = 1, N
      omni_trace = omni_trace + A(i,i)
    end do
  end function omni_trace

  ! 3x3 determinant
  double precision function omni_det_3x3(A)
    double precision, intent(in) :: A(3,3)
    omni_det_3x3 = A(1,1)*(A(2,2)*A(3,3) - A(2,3)*A(3,2)) &
                 - A(1,2)*(A(2,1)*A(3,3) - A(2,3)*A(3,1)) &
                 + A(1,3)*(A(2,1)*A(3,2) - A(2,2)*A(3,1))
  end function omni_det_3x3

end module omni_hpc_matrix
