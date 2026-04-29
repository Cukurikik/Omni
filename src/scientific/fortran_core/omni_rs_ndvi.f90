! Omni RS-SpatioTemporal NDVI Compute (Fortran)
! Ref: Chen-Yang-Liu/Awesome-RS-SpatioTemporal-VLMs
module omni_rs_ndvi
  implicit none
contains
  pure function compute_ndvi(nir, red) result(ndvi)
    real(8), intent(in) :: nir, red
    real(8) :: ndvi
    if (abs(nir + red) > 1.0d-8) then
      ndvi = (nir - red) / (nir + red)
    else
      ndvi = 0.0d0
    end if
  end function

  pure function change_magnitude(t1, t2, n) result(mag)
    integer, intent(in) :: n
    real(8), intent(in) :: t1(n), t2(n)
    real(8) :: mag
    integer :: i
    mag = 0.0d0
    do i = 1, n
      mag = mag + (t2(i) - t1(i))**2
    end do
    mag = sqrt(mag / max(n, 1))
  end function
end module
