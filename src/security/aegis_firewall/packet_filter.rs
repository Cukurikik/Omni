use omni_std::result::{Result, Ok, Err};
use std::net::Ipv4Addr;

pub fn filter_packet(src: Ipv4Addr, port: u16, payload: &[u8]) -> Result<bool, String> {
    if payload.len() > 1500 {
        return Err("Payload exceeds MTU, possible buffer attack".to_string());
    }
    Ok(true)
}
