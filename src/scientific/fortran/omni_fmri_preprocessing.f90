! OMNI Framework - fMRI Preprocessing in Fortran
! Zero-mock HPC preprocessing before piping data into BolT transformers.

module omni_fmri_preprocessing
    implicit none

contains

    subroutine normalize_timeseries(data, time_steps, regions)
        integer, intent(in) :: time_steps, regions
        real(8), dimension(time_steps, regions), intent(inout) :: data
        integer :: r
        real(8) :: mean_val, std_val

        do r = 1, regions
            ! Calculate Mean
            mean_val = sum(data(:, r)) / real(time_steps, 8)
            
            ! Calculate Standard Deviation
            std_val = sqrt(sum((data(:, r) - mean_val)**2) / real(time_steps - 1, 8))
            
            ! Apply Z-score Normalization
            if (std_val > 1e-6) then
                data(:, r) = (data(:, r) - mean_val) / std_val
            else
                data(:, r) = 0.0_8
            end if
        end do
    end subroutine normalize_timeseries

end module omni_fmri_preprocessing
