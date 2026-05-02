// @omni-domain System Layer (Quantization Runtime)
// @omni-source OpenGVLab/OmniQuant
// @omni-description OmniQuant Quantizer mimicking int4 weight packing in Rust.
// @omni-requirement zero-mock, monadic-error
pub enum QuantError { InvalidBits, EmptyWeights }
pub type OmniResult<T> = Result<T, QuantError>;

pub fn pack_int4(values: &[u8]) -> OmniResult<Vec<u8>> {
    if values.is_empty() { return Err(QuantError::EmptyWeights); }
    let mut packed = Vec::with_capacity((values.len() + 1) / 2);
    for chunk in values.chunks(2) {
        let hi = chunk[0] & 0x0F;
        let lo = if chunk.len() > 1 { chunk[1] & 0x0F } else { 0 };
        packed.push((hi << 4) | lo);
    }
    Ok(packed)
}

pub fn unpack_int4(packed: &[u8], count: usize) -> OmniResult<Vec<u8>> {
    if packed.is_empty() { return Err(QuantError::EmptyWeights); }
    let mut result = Vec::with_capacity(count);
    for &byte in packed {
        result.push((byte >> 4) & 0x0F);
        if result.len() < count { result.push(byte & 0x0F); }
    }
    result.truncate(count);
    Ok(result)
}
