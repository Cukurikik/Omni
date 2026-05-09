# omni_kinematics_chain.jl — Forward Kinematics Chain
# Layer: Domain / Julia
#
# Computes the forward kinematics for a multi-link robotic chain
# using Denavit-Hartenberg parameters to calculate end-effector pose.

module OmniKinematicsChain

export DHParameter, transform_matrix, compute_chain_pose

using LinearAlgebra

"""
Denavit-Hartenberg parameters for a single link
θ: Joint angle (Z-axis rotation)
d: Link offset (Z-axis translation)
a: Link length (X-axis translation)
α: Link twist (X-axis rotation)
"""
struct DHParameter
    theta::Float64
    d::Float64
    a::Float64
    alpha::Float64
end

"""
Computes the 4x4 homogeneous transformation matrix for a single DH link.
"""
function transform_matrix(dh::DHParameter)
    ct = cos(dh.theta)
    st = sin(dh.theta)
    ca = cos(dh.alpha)
    sa = sin(dh.alpha)
    
    # Standard DH transformation matrix
    T = [
        ct  -st*ca  st*sa   dh.a*ct;
        st   ct*ca -ct*sa   dh.a*st;
        0.0  sa     ca      dh.d;
        0.0  0.0    0.0     1.0
    ]
    return T
end

"""
Computes the final pose (4x4 matrix) of the end effector by multiplying
the transformation matrices of all links in the chain.
"""
function compute_chain_pose(chain::Vector{DHParameter})
    # Start with Identity matrix
    T_final = Matrix{Float64}(I, 4, 4)
    
    for dh in chain
        T_link = transform_matrix(dh)
        T_final = T_final * T_link
    end
    
    return T_final
end

"""
Extracts Cartesian position (X, Y, Z) from a 4x4 transformation matrix.
"""
function extract_position(T::Matrix{Float64})
    return [T[1,4], T[2,4], T[3,4]]
end

end # module
