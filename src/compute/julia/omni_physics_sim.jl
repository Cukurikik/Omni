module OmniPhysicsSim

using LinearAlgebra

struct Particle
    mass::Float64
    position::Vector{Float64}
    velocity::Vector{Float64}
end

function compute_gravitational_forces(particles::Vector{Particle}, G::Float64 = 6.67430e-11)
    n = length(particles)
    forces = [zeros(Float64, 3) for _ in 1:n]
    
    for i in 1:n
        for j in (i+1):n
            p1 = particles[i]
            p2 = particles[j]
            
            r_vec = p2.position - p1.position
            distance = norm(r_vec)
            
            if distance > 1e-5
                force_mag = G * (p1.mass * p2.mass) / (distance^2)
                force_vec = force_mag * (r_vec / distance)
                
                forces[i] += force_vec
                forces[j] -= force_vec
            end
        end
    end
    return forces
end

function step_simulation!(particles::Vector{Particle}, dt::Float64)
    forces = compute_gravitational_forces(particles)
    for i in 1:length(particles)
        acceleration = forces[i] / particles[i].mass
        particles[i].velocity .+= acceleration * dt
        particles[i].position .+= particles[i].velocity * dt
    end
end

end # module
