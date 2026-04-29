module TLSInspector

export OmniResult, compute_sni_offset

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

# Deterministic Deep Packet Inspection Math
# Locating the Server Name Indication (SNI) extension in a TLS ClientHello
function compute_sni_offset(packet_len::Int, session_id_len::Int, cipher_suites_len::Int, comp_methods_len::Int) :: OmniResult{Int, String}
    # Mathematical representation of TLS 1.2/1.3 ClientHello fixed and variable boundaries
    # Record Header (5) + Handshake Header (4) + Version (2) + Random (32) = 43 bytes base offset
    
    base_offset = 43
    
    # Verify sanity
    if session_id_len < 0 || session_id_len > 32
        return OmniResult("Invalid session ID length", Int)
    end
    
    # Calculate offset to extensions length field
    # 1 byte for session_id_len + session_id_len + 2 bytes for cipher_suites_len + cipher_suites_len + 1 byte for comp_methods_len + comp_methods_len
    extensions_offset = base_offset + 1 + session_id_len + 2 + cipher_suites_len + 1 + comp_methods_len
    
    if extensions_offset + 2 > packet_len
        return OmniResult("Packet too short to contain TLS extensions", Int)
    end
    
    # We return the calculated offset where the extension parsing engine should start scanning for SNI (Type 0x0000)
    return OmniResult(extensions_offset + 2)
end

end
