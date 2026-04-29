module StrangeletParticleContainment

export OmniResult, compute_color_flavor_locked_phase

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
    is_ok::Bool
end

function OmniResult(value::T) where T
    OmniResult{T, String}(value, nothing, true)
end

function OmniResult(error::String, ::Type{T}=Any) where T
    OmniResult{T, String}(nothing, error, false)
end

# Deterministic calculation of Color-Flavor Locked Superconducting Quark Matter.
# A Strangelet is a hypothetical particle made of Up, Down, and Strange quarks.
# At extreme densities, it enters a "Color-Flavor Locked" (CFL) phase, becoming a perfect
# superconductor. It is theoretically more stable than normal matter, meaning if a
# strangelet touches normal matter, it could convert it all into strange matter (Ice-9 scenario).
function compute_color_flavor_locked_phase(baryon_chemical_potential_mev::Float64, strange_quark_mass_mev::Float64) :: OmniResult{Float64, String}
    if baryon_chemical_potential_mev <= 0.0 || strange_quark_mass_mev <= 0.0
        return OmniResult("Invalid quark parameters", Float64)
    end
    
    # Physics: For CFL phase to exist, the gap energy (Delta) must be greater than
    # the strange quark mass penalty (m_s^2 / 2 * mu)
    
    # Simulated gap energy
    cfl_gap_energy = 100.0 # MeV
    
    mass_penalty = (strange_quark_mass_mev^2) / (2.0 * baryon_chemical_potential_mev)
    
    stability_margin = cfl_gap_energy - mass_penalty
    
    return OmniResult(stability_margin)
end

end
