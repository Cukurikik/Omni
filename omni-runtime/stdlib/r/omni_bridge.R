# ============================================================
# OMNI R Bridge — Statistical Compute Nexus
# ============================================================
# Layer: Compute (Statistics, Probability, Modeling)
# R menggunakan .Call bawaan — TIDAK perlu install.packages().
# ============================================================

.omni_lib_loaded <- FALSE
.omni_lib_path <- NULL

#' Inisialisasi OMNI Kernel
#' @export
omni_init <- function() {
  ext <- switch(Sys.info()["sysname"],
    Windows = "omni_core.dll",
    Darwin  = "libomni_core.dylib",
    "libomni_core.so"
  )

  lib_path <- file.path(dirname(sys.frame(1)$ofile),
                         "..", "..", "core", "target", "release", ext)

  if (!file.exists(lib_path)) {
    stop(sprintf("[OMNI-E701] Kernel tidak ditemukan: %s\nKompilasi: omni build --release", lib_path))
  }

  dyn.load(lib_path)
  .omni_lib_loaded <<- TRUE
  .omni_lib_path <<- lib_path
  message("[OMNI] Kernel R bridge terinisialisasi.")
}

#' Eksekusi fungsi OMNI dari R
#'
#' @param func_name Nama fungsi di registry OMNI
#' @param data Raw vector (byte array)
#' @return External pointer dari kernel Rust
#' @export
omni_execute <- function(func_name, data) {
  if (!.omni_lib_loaded) {
    stop("[OMNI-E702] Kernel belum diinisialisasi. Jalankan omni_init() terlebih dahulu.")
  }

  if (!is.raw(data)) {
    data <- as.raw(data)
  }

  result <- .Call("__omni_ffi", data, length(data))

  if (is.null(result)) {
    stop("[OMNI-E703] Kernel mengembalikan NULL")
  }

  return(result)
}

#' Kirim matriks R langsung ke Rust tanpa copy
#'
#' @param mat Matriks numerik R
#' @return External pointer
#' @export
omni_execute_matrix <- function(mat) {
  if (!is.matrix(mat) || !is.numeric(mat)) {
    stop("[OMNI-E704] Input harus numeric matrix")
  }

  # R matrix disimpan column-major — Rust akan membacanya sebagai flat f64 array
  raw_bytes <- writeBin(as.double(mat), raw(), size = 8)
  return(omni_execute("r_stat_dispatch", raw_bytes))
}
