module CourseRecommender

using LinearAlgebra

function compute_similarity(user_vector::Vector{Float64}, course_vectors::Matrix{Float64})
    # Cosine similarity for course recommendations
    scores = Float64[]
    u_norm = norm(user_vector)
    for i in 1:size(course_vectors, 2)
        c_vec = course_vectors[:, i]
        sim = dot(user_vector, c_vec) / (u_norm * norm(c_vec))
        push!(scores, sim)
    end
    return scores
end

end
