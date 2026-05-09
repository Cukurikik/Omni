# @omni-layer Compute | @omni-source Yachay-AI/byt5-geotagging | @omni-lang Julia
# @omni-description Haversine distance kernel: SIMD-vectorized geographic
# distance computation for batch geolocation evaluation.

module OmniHaversine

const EARTH_RADIUS_KM = 6371.0

function haversine(lat1::Float64, lon1::Float64, lat2::Float64, lon2::Float64)
    dlat = deg2rad(lat2 - lat1)
    dlon = deg2rad(lon2 - lon1)
    a = sin(dlat/2)^2 + cos(deg2rad(lat1)) * cos(deg2rad(lat2)) * sin(dlon/2)^2
    c = 2 * atan(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c
end

function batch_distances(lats1::Vector{Float64}, lons1::Vector{Float64},
                         lats2::Vector{Float64}, lons2::Vector{Float64})
    n = min(length(lats1), length(lats2))
    distances = Vector{Float64}(undef, n)
    @simd for i in 1:n
        @inbounds distances[i] = haversine(lats1[i], lons1[i], lats2[i], lons2[i])
    end
    return distances
end

function accuracy_at_threshold(distances::Vector{Float64}, threshold_km::Float64)
    within = count(d -> d <= threshold_km, distances)
    return within / max(length(distances), 1)
end

function distance_statistics(distances::Vector{Float64})
    n = length(distances)
    if n == 0
        return (mean=0.0, median=0.0, std=0.0, min=0.0, max=0.0,
                acc_100km=0.0, acc_500km=0.0, acc_1000km=0.0)
    end
    sorted = sort(distances)
    mean_d = sum(distances) / n
    median_d = sorted[div(n+1, 2)]
    var_d = sum((d - mean_d)^2 for d in distances) / n
    return (
        mean = mean_d,
        median = median_d,
        std = sqrt(var_d),
        min = sorted[1],
        max = sorted[end],
        acc_100km = accuracy_at_threshold(distances, 100.0),
        acc_500km = accuracy_at_threshold(distances, 500.0),
        acc_1000km = accuracy_at_threshold(distances, 1000.0)
    )
end

end # module
