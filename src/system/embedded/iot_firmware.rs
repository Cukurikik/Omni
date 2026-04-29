#![no_std]
#![no_main]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

pub struct OmniIotSensor {
    pub id: u32,
    pub active: bool,
}

impl OmniIotSensor {
    pub fn new(id: u32) -> Self {
        Self { id, active: true }
    }

    pub fn read_temperature(&self) -> Result<f32, &'static str> {
        if !self.active {
            return Err("Sensor is inactive");
        }
        // Simulated I2C hardware read
        Ok(24.5)
    }
}
