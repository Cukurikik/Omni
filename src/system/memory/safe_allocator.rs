use std::alloc::{GlobalAlloc, Layout, System};

pub struct OmniSafeAllocator;

unsafe impl GlobalAlloc for OmniSafeAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let ptr = System.alloc(layout);
        if !ptr.is_null() {
            // Zero initialize memory for safety (Vaex zero-copy reqs)
            std::ptr::write_bytes(ptr, 0, layout.size());
        }
        ptr
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        System.dealloc(ptr, layout)
    }
}

#[global_allocator]
static ALLOCATOR: OmniSafeAllocator = OmniSafeAllocator;
