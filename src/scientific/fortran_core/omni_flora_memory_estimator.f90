// Omni Flora Memory Estimator (Fortran)
// Ref: BorealisAI/flora-opt — ICML 2024
program omni_flora_memory
  implicit none
  integer :: model_dim, proj_dim, n_params
  real(8) :: full_memory_mb, flora_memory_mb, savings
  model_dim = 4096; proj_dim = 256; n_params = 7000000000
  full_memory_mb = n_params * 8.0d0 / (1024.0d0 * 1024.0d0)
  flora_memory_mb = (n_params / model_dim) * proj_dim * 8.0d0 / (1024.0d0 * 1024.0d0)
  savings = 1.0d0 - flora_memory_mb / full_memory_mb
  print *, "Full memory (MB):", full_memory_mb
  print *, "Flora memory (MB):", flora_memory_mb
  print *, "Savings ratio:", savings
end program omni_flora_memory
