# Omni FineR Tensor Stats (AWK)
# Compute Layer: Fast deterministic statistical aggregation for visual tensors.

BEGIN {
    total_elements = 0;
    max_val = -99999.0;
    min_val = 99999.0;
    sum = 0.0;
}

{
    val = $1;
    total_elements++;
    sum += val;
    if (val > max_val) max_val = val;
    if (val < min_val) min_val = val;
}

END {
    if (total_elements > 0) {
        printf "OMNI_FINER_STATS: elements=%d min=%f max=%f avg=%f\n", total_elements, min_val, max_val, sum / total_elements;
    } else {
        printf "OMNI_FINER_STATS: EMPTY_TENSOR\n";
    }
}
