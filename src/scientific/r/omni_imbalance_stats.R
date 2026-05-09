# OMNI MOTHER: R Statistical Modeling for MoE Imbalance

compute_imbalance <- function(loads) {
    if (length(loads) == 0) return(1.0)
    
    mean_load <- mean(loads)
    if (mean_load == 0) return(1.0)
    
    variance <- var(loads) * (length(loads) - 1) / length(loads) # population variance
    cv_sq <- variance / (mean_load^2)
    
    return(1.0 + cv_sq)
}
