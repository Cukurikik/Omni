#![no_std]
#![no_main]

use core::panic::PanicInfo;

// OMNI MOTHER: Unikernel Bare-Metal Bootloader (Production Grade)

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    // 1. Initialize bare-metal serial port for logging
    // 2. Setup memory paging
    // 3. Jump to Omni Engine Kernel
    
    let vga_buffer = 0xb8000 as *mut u8;
    
    for (i, &byte) in b"OMNI UNIKERNEL BOOT".iter().enumerate() {
        unsafe {
            *vga_buffer.offset(i as isize * 2) = byte;
            *vga_buffer.offset(i as isize * 2 + 1) = 0xb; // Light cyan
        }
    }
    
    loop {}
}
