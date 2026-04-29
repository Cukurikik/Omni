# PointLLM — 3D Feature Statistics in R
omni_result <- function(is_ok, value = NULL, error = NULL) list(is_ok = is_ok, value = value, error = error)
compute_point_cloud_stats <- function(coords) {
  if (is.null(coords) || nrow(coords) == 0) return(omni_result(FALSE, error = "Empty coordinates"))
  if (ncol(coords) != 3) return(omni_result(FALSE, error = "Expected 3 columns (x,y,z)"))
  if (nrow(coords) > 10000000) return(omni_result(FALSE, error = "Points exceed 10M"))
  centroid <- colMeans(coords)
  bbox_min <- apply(coords, 2, min)
  bbox_max <- apply(coords, 2, max)
  volume <- prod(bbox_max - bbox_min)
  return(omni_result(TRUE, value = list(centroid = centroid, bbox_min = bbox_min, bbox_max = bbox_max, volume = volume, n_points = nrow(coords))))
}
